import os
import asyncio
import glob

import aiohttp
from aiofile import async_open

from .async_base import AsyncWeb
from .fake_array import FakeStringArray, LengthError


class AsyncDownloader(AsyncWeb):
    """Async File Downloader"""

    def __init__(
            self,
            connections_limit=20,
            allow_redirects=False,
            skip_checking=False,
            keep_alive=True,
            keep_alive_timeout: None | float | object = 30
    ):
        super().__init__(connections_limit, allow_redirects, keep_alive, keep_alive_timeout)

        self._urls = None
        self._download_folder_parent = './download'
        self._download_subfolders = None
        self._remove_empty_folders = True
        self.skip_checking = skip_checking

        self._filenames = None
        self._filenames_as_prefix = False
        self._filenames_separator = '-'
        self._filenames_keep_extension = True

        self._check_folder_parent = None
        self._check_subfolders = None
        self._check_any_extension = False

    def set_download_folder(self, folder: str, subfolders: str | list | tuple = None, remove_empty_folders=True):
        """Optional setting to set downloading folder"""

        self._download_folder_parent = folder.strip().rstrip(r'.\/')
        self._remove_empty_folders = remove_empty_folders
        if subfolders:
            self._download_subfolders = FakeStringArray(subfolders, True)
        return self

    def set_check_folder(self, parent: str, subfolders: str | list | tuple = None, any_extension=False):
        """Optional setting to set additional folder to check files in it"""

        self._check_folder_parent = parent.strip().rstrip(r'.\/')
        self._check_any_extension = any_extension
        if subfolders:
            self._check_subfolders = FakeStringArray(subfolders, True)
        return self

    def set_filenames(self, filenames: str | list | tuple, as_prefix=False, prefix_separator='-', keep_extension=True):
        """Optional setting to set names of files"""

        self._filenames = FakeStringArray(filenames)
        self._filenames_as_prefix = as_prefix
        self._filenames_separator = prefix_separator
        self._filenames_keep_extension = keep_extension
        return self

    def run(self, urls, folder=None):
        """Sync start of downloading"""
        return asyncio.run(self.run_async(urls, folder))

    async def run_async(self, urls, folder):
        """Async start of downloading"""
        self._urls = FakeStringArray(urls)
        if folder:
            self.set_download_folder(folder)

        self._check_lengths()
        self._create_download_folders()

        connector = aiohttp.TCPConnector(limit=self.connections_limit,
                                         force_close=not self.keep_alive,
                                         keepalive_timeout=self.keep_alive_timeout)

        async with aiohttp.ClientSession(connector=connector) as session:
            session.headers.update(self.headers)
            session.cookie_jar.update_cookies(self.cookies)

            tasks = (self._prepare_download(session, ind) for ind in range(len(urls)))

            await self._start_tasks_limited(tasks, length=len(urls), ignore_output=True)

        self._print_errors()

        if self._remove_empty_folders:
            self._clear_empty_subfolders()

    async def _prepare_download(self, session, index):
        """
        Preparing to download file.
        Definition of path and name of file.
        Checking file existence in folders.
        """
        url = self._urls[index]
        if not url:
            return

        name = url.split('/')[-1].split('?')[0]
        filename, ext = os.path.splitext(name)

        if self._filenames:
            if self._filenames_as_prefix:
                name = self._filenames[index] + self._filenames_separator + filename
            else:
                name = self._filenames[index]

            if self._filenames_keep_extension:
                name += ext

        folder = self._download_folder_parent
        if self._download_subfolders:
            folder = os.path.join(folder, self._download_subfolders[index])

        filepath = os.path.join(folder, name)
        if self.skip_checking:
            return await self._start_download(session, url, filepath)

        exists_in_download = await self._check_file_in_folder(folder, name)
        exists_in_check = False

        if not exists_in_download and self._check_folder_parent:
            check_folder = self._check_folder_parent
            if self._check_subfolders:
                check_folder = os.path.join(check_folder, self._check_subfolders[index])

            exists_in_check = await self._check_file_in_folder(check_folder, name, self._check_any_extension)

        if not any((exists_in_download, exists_in_check)):
            return await self._start_download(session, url, filepath)

    async def _start_download(self, session: aiohttp.ClientSession, url, filepath):
        """Starting of file downloading"""

        @self.try_decorator(url)
        async def load_image():
            async with session.get(url, allow_redirects=self.allow_redirects) as r:
                if r.status == 200:
                    data = await r.read()
                    if len(data) > 0:
                        await self._save_file(filepath, data)
                        return
                    else:
                        self._add_error_info("File size is too low:" + str(len(data)), url)
                        return
                else:
                    r.raise_for_status()

        await load_image()

    def _check_lengths(self):
        """Checking list lengths"""

        base_str = ('The length of download links list does not match the length of {} list.\n'
                    'Allowed to use [str | list[str] | tuple[str]]')

        if self._filenames and not self._urls.compare_length(self._filenames):
            raise LengthError(
                base_str.format('names')
            )
        if self._download_subfolders and not self._urls.compare_length(self._download_subfolders):
            raise LengthError(
                base_str.format('download subfolders')
            )
        if self._check_subfolders and not self._urls.compare_length(self._check_subfolders):
            raise LengthError(
                base_str.format('check subfolders')
            )

    def _create_download_folders(self):
        parent_folder = self._download_folder_parent
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder)

        if self._download_subfolders:
            for f in set(self._download_subfolders):
                folder = os.path.join(parent_folder, f)
                if not os.path.exists(folder):
                    os.makedirs(folder)

    def _clear_empty_subfolders(self):
        parent_folder = self._download_folder_parent
        if self._download_subfolders:
            for f in set(self._download_subfolders):
                folder = os.path.join(parent_folder, f)
                if os.path.exists(folder) and not os.listdir(folder.strip()):
                    os.rmdir(folder)
        if os.path.exists(parent_folder) and not os.listdir(parent_folder.strip()):
            os.rmdir(parent_folder)
            return

    @staticmethod
    async def _check_file_in_folder(folder, name, any_ext=False):
        filepath = os.path.join(folder, name)
        if any_ext:
            return os.path.exists(filepath) or bool(glob.glob(glob.escape(os.path.splitext(filepath)[0] + '.*')))

        return os.path.exists(filepath)

    @staticmethod
    async def _save_file(filepath, data):
        async with async_open(filepath, 'wb') as f:
            await f.write(data)
