from pprint import pprint
# pip install lxml
# pip install beautifulsoup4
from bs4 import BeautifulSoup

from async_parse_tools import AsyncRequests, ClientSession

urls = tuple(f'https://www.istockphoto.com/en/search/2/image?phrase=cats&page={x}' for x in range(5))


async def parse(url: str, r: bytes, session: ClientSession):
    bs = BeautifulSoup(r, "lxml")
    images = bs.findAll('picture')
    urls = [x.find('img').get('src') for x in images]
    return urls


out = (AsyncRequests(connections_limit=5)
       .error_settings(max_tries=2)
       # .set_user_agent()
       # .set_cookies()
       # .set_headers()
       .run(urls, parse))

pprint(out[0])
