import asyncio
from enum import Enum

from .async_base import AsyncWeb
from typing import Awaitable, Any, Callable

from playwright.async_api import async_playwright, Page, BrowserContext, Browser, Route


class BrowserType(Enum):
    CHROMIUM = 'chromium'
    FIREFOX = 'firefox'
    WEBKIT = 'webkit'


class AsyncBrowser(AsyncWeb):
    def __init__(self, connections_limit=20):
        super().__init__(connections_limit)
        self.func = None

        self.browser_headless = True
        self.browser_type = BrowserType.CHROMIUM
        self.browser_disable_images = True

    def set_browser_settings(self, browser_type=BrowserType.CHROMIUM, headless=True, disable_images=True):
        self.browser_headless = headless
        self.browser_type = browser_type
        self.browser_disable_images = disable_images
        return self

    def run(self, urls, func: Callable[[str, Page], Awaitable[Any]]):
        return asyncio.run(self.run_async(urls, func))

    async def run_async(self, urls, func: Callable[[str, Page], Awaitable[Any]]):
        self.func = func
        async with async_playwright() as p:
            browser, context = await self._start_browser(p)

            tasks = []
            for url in urls:
                tasks.append(self._open_page(context, url))

            out = await self._start_tasks_limited(tasks, limit=self.connections_limit)
            self._print_errors()

            await browser.close()
            return out

    async def _start_browser(self, p) -> tuple[Browser, BrowserContext]:
        browser: Browser = await getattr(p, self.browser_type.value).launch(headless=self.browser_headless)
        context = await browser.new_context(user_agent=self.headers.get('User-Agent'))
        if self.cookies:
            await context.add_cookies(cookies=self.cookies)
        return browser, context

    async def _open_page(self, context: BrowserContext, url: str):
        page = await self._create_new_page(context)

        @self.try_decorator(url)
        async def get_info():
            await page.goto(url)
            return await self.func(url, page)

        out = await get_info()

        await page.close()
        return out

    async def _create_new_page(self, context: BrowserContext) -> Page:
        page = await context.new_page()
        await page.set_extra_http_headers(self.headers)
        if self.browser_disable_images:
            await page.route("**/*", self._hide_images)
        return page

    @staticmethod
    def _hide_images(route: Route):
        if route.request.resource_type == "image":
            return route.abort()
        return route.continue_()
