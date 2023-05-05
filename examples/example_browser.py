import asyncio

from async_parse_tools import AsyncBrowser, Page


async def test_func(url, page: Page):
    # page.locator()
    await asyncio.sleep(2)
    return await page.title()


urls = ['https://www.whatismybrowser.com/detect/what-is-my-user-agent/',
        'https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending']

# os.environ['PWDEBUG'] = '0'
b = (AsyncBrowser(connections_limit=5)
     .error_settings(max_tries=3)
     .visuals_settings(use_statusbar=True, use_ascii=False, print_errors_string=True)
     .set_browser_settings(headless=False)
     .set_user_agent('Mozilla/5.0 (Linux; Android 13; LM-Q710(FGN)) '
                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/107.0.5304.91 Mobile Safari/537.36')
     .set_headers({'1test-header': 'blablabla'}))
out = b.run(urls, test_func)
print(out)

out = b.run(urls, test_func)
print(out)
