import asyncio
from typing import Callable, Any, Awaitable

import aiohttp
from aiohttp import ClientSession

from .async_base import AsyncWeb
from .fake_array import FakeArray, FakeStringArray, LengthError


class AsyncRequests(AsyncWeb):
    def __init__(
            self,
            request_method='get',
            request_kwargs: tuple[dict] | list[dict] | dict | None = None,
            connections_limit=20,
            allow_redirects=False,
            keep_alive=True,
            keep_alive_timeout: None | float | object = 30
    ):
        super().__init__(connections_limit, allow_redirects, keep_alive, keep_alive_timeout)

        self.request_method = request_method
        if request_kwargs is not None:
            self.request_kwargs = FakeArray(request_kwargs)
        else:
            self.request_kwargs = FakeArray({})

        self.urls = None
        self.callback_function = None

    def _check_lengths(self):
        base_str = 'The length of requests urls list does not match the length of {} list.'

        if self.request_kwargs and not self.urls.compare_length(self.request_kwargs):
            raise LengthError(base_str.format('request_kwargs'))

    def run(self, urls, callback_function: Callable[[str, bytes, ClientSession], Awaitable[Any]]):
        return asyncio.run(self.run_async(urls, callback_function))

    async def run_async(self, urls, callback_function: Callable[[str, bytes, ClientSession], Awaitable[Any]]):
        self.urls = FakeStringArray(urls)
        self.callback_function = callback_function
        self._check_lengths()

        connector = aiohttp.TCPConnector(limit=self.connections_limit,
                                         force_close=not self.keep_alive,
                                         keepalive_timeout=self.keep_alive_timeout)

        async with aiohttp.ClientSession(connector=connector) as session:
            session.headers.update(self.headers)
            session.cookie_jar.update_cookies(self.cookies)

            tasks = [self._load_info(session, index) for index in range(len(urls))]
            output = await self._start_tasks(tasks)

        self._print_errors()

        return output

    async def _load_info(self, session: ClientSession, index):

        url = self.urls[index]

        @self.try_decorator(url)
        async def parse_info():
            async with session.request(self.request_method, url, allow_redirects=self.allow_redirects,
                                       **self.request_kwargs[index]) as res:
                res.raise_for_status()
                r = await res.read()
                return await self.callback_function(url, r, session)

        return await parse_info()
