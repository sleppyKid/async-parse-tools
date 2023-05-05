Every class from below inherits from AsyncBase abd AsyncWeb and supports additional settings

```python
from async_parse_tools import AsyncBase, AsyncWeb

(
    AsyncWeb(connections_limit=5, allow_redirects=True)
    # From AsyncBase
    .error_settings(max_tries=5, error_wait_time=2, return_errors=False)
    .visuals_settings(use_statusbar=True, use_ascii=True, print_errors_string=True)
    # From AsyncWeb
    .set_headers()
    .set_user_agent()
    .set_cookies()
    # To export cookies from browser to json use extension:
    # https://github.com/ktty1220/export-cookie-for-puppeteer
)

# If return_errors is True, run and run_async returns tuple(output, list[errors])

output = AsyncBase().error_settings(return_errors=False).run()
output, errors = AsyncBase().error_settings(return_errors=True).run()


```

## async_downloader

```python
from async_parse_tools import AsyncDownloader

urls = [
    'url_to_photo1.jpg',
    'url_to_photo2.jpg',
    'url_to_photo3.jpg'
]

# Simple usage example:
AsyncDownloader().run(urls=urls, folder='./files/')

# Extended usage example:

list_of_subfolders = ['1', '2', '3']

(
    AsyncDownloader()
    .set_filenames('test-prefix', as_prefix=True)
    .set_download_folder('./download', list_of_subfolders)
    .set_check_folder('./check', list_of_subfolders)
    .run(urls)
)
```

## async_browser

```python
from async_parse_tools import AsyncBrowser, Page, BrowserType, load_json

urls = [
    'https://www.whatismybrowser.com/detect/what-is-my-user-agent/',
    'https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending'
]


async def parse_func(url: str, page: Page):
    # page.locator()
    return await page.title()


# Simple usage example:
out = AsyncBrowser().run(urls=urls, func=parse_func)

# Extended usage example:

cookies = load_json('cookies.txt')

out = (
    AsyncBrowser()
    .set_browser_settings(browser_type=BrowserType.CHROMIUM, headless=True, disable_images=True)
    .set_cookies(cookies)
    .run(urls=urls, func=parse_func)
)

```

## async_requests

```python
from async_parse_tools import (AsyncRequests, ClientSession, load_json,
                               load_json_cookies_as_dict, convert_cookies_to_dict)
from bs4 import BeautifulSoup

urls = tuple(f'https://www.istockphoto.com/en/search/2/image?phrase=cats&page={x}' for x in range(5))


async def parse(url: str, r: bytes, session: ClientSession):
    bs = BeautifulSoup(r, "lxml")
    images = bs.findAll('picture')
    urls = [x.find('img').get('src') for x in images]
    return urls


cookies = load_json('cookies.txt')
cookies_req = convert_cookies_to_dict(cookies)
# or
cookies_req = load_json_cookies_as_dict('cookies.txt')

out = (
    AsyncRequests(connections_limit=5)
    .set_cookies(cookies_req)  # Optional
    .run(urls=urls, callback_function=parse)
)

```