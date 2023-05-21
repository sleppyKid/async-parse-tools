import asyncio
import gc

from asyncio_pool import AioPool
import platform
from abc import abstractmethod, ABC
from functools import wraps
from typing import Generator, Iterable

import tqdm
import tqdm.asyncio

from .utils import get_random_user_agent


class AsyncBase(ABC):
    """
    Абстрактный класс, объявляющий интерфейс и добавляющий базовые функции
    """

    def __init__(self):
        self.use_statusbar = True
        self.statusbar_ascii = False
        self.print_errors_string = True

        self.errors = []
        self.max_tries = 5
        self.error_wait_time = 2
        self.return_errors = False

        self.run_async = self._return_decorator(self.run_async)

    def visuals_settings(self, use_statusbar=True, use_ascii=False, print_errors_string=True):
        self.use_statusbar = use_statusbar
        self.statusbar_ascii = use_ascii
        self.print_errors_string = print_errors_string
        return self

    def error_settings(self, max_tries=5, error_wait_time=2, return_errors=False):
        """
        If return_errors is True, run and run_async returns tuple(output, list[errors])
        """
        self.max_tries = max_tries
        self.error_wait_time = error_wait_time
        self.return_errors = return_errors
        return self

    def _return_decorator(self, func):
        @wraps(func)
        async def inner(*args, **kwargs):
            output = await func(*args, **kwargs)
            if self.return_errors:
                return output, self.errors
            return output

        return inner

    def windows_fix(self):
        if platform.system() == 'Windows':
            current_policy = asyncio.get_event_loop_policy()
            if not isinstance(current_policy, asyncio.WindowsSelectorEventLoopPolicy):
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return self

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    @abstractmethod
    async def run_async(self, *args, **kwargs):
        pass

    async def _start_tasks(self, tasks):
        """Простой метод запуска выполнения заданий"""

        awaited_tasks = (asyncio.create_task(t) for t in tasks)
        if self.use_statusbar:
            output = await tqdm.asyncio.tqdm.gather(*awaited_tasks, ascii=self.statusbar_ascii)
        else:
            output = await asyncio.gather(*awaited_tasks)

        return output

    async def _start_tasks_limited(self, tasks: Generator | Iterable, limit=100, length=None,
                                   gc_size=2000, ignore_output=False):
        """Метод запуска заданий с ограничением одновременных выполнений(потоков)"""

        if length is None:
            length = len(tasks)

        awaited_tasks = []
        async with AioPool(size=limit) as pool:
            if self.use_statusbar:
                with tqdm.tqdm(total=length, ascii=self.statusbar_ascii) as pbar:
                    for t in tasks:
                        fut = await pool.spawn(t)
                        pbar.update()

                        if not ignore_output:
                            awaited_tasks.append(fut)

                        if not pbar.n % gc_size:
                            gc.collect()

            else:
                count = 0
                for t in tasks:
                    count += 1
                    fut = await pool.spawn(t)

                    if not ignore_output:
                        awaited_tasks.append(fut)

                    if not count % gc_size:
                        gc.collect()

        if ignore_output:
            return None

        return tuple(x.result() for x in awaited_tasks)

    def try_decorator(self, error_context=None):
        def try_decorator_inner(f):
            async def try_again(*args, **kwargs):
                self.errors.clear()
                tries = self.max_tries
                while tries:
                    try:
                        return await f(*args, **kwargs)
                    except Exception as e:
                        tries -= 1
                        last_error = (e, error_context)
                        if tries:
                            await asyncio.sleep(self.error_wait_time)
                        else:
                            self._add_error_info(*last_error)

            return try_again

        return try_decorator_inner

    def _add_error_info(self, error, task_info):
        self.errors.append((error, task_info))

    def count_errors(self):
        message = {}
        for e in self.errors:
            if e:
                key = e[0].__class__.__name__ if isinstance(e[0], Exception) else e[0]
                message[key] = message.get(key, 0) + 1
        return message

    def get_errors_string(self):
        return ', '.join(f'{k}: {v}' for k, v in self.count_errors().items())

    def _print_errors(self):
        if self.print_errors_string and self.errors:
            print(self.get_errors_string())


def concurrency_limit(n=3):
    """Декоратор ограничивающий количество одновременных активных задач"""
    sem = asyncio.Semaphore(value=n)

    def executor(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with sem:
                return await func(*args, **kwargs)

        return wrapper

    return executor


class AsyncWeb(AsyncBase, ABC):
    """Абстрактный класс, реализующий стандартные настройки для работы с сетью"""

    def __init__(self, connections_limit=20, allow_redirects=False, keep_alive=False):
        super().__init__()
        self.connections_limit = connections_limit
        self.allow_redirects = allow_redirects
        self.keep_alive = keep_alive
        self.user_agent = get_random_user_agent()
        self._headers = {}
        self.cookies = {}

    @property
    def headers(self):
        return {"User-Agent": self.user_agent} | self._headers

    def set_headers(self, headers: dict):
        """Установка заголовков запроса"""

        self._headers = headers
        return self

    def set_cookies(self, cookies: dict):
        """Установка cookie запроса"""

        self.cookies = cookies
        return self

    def set_user_agent(self, user_agent: str):
        """Установка User-Agent в заголовке"""

        self.user_agent = user_agent
        return self
