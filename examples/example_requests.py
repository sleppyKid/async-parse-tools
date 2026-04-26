import asyncio
import json
from pprint import pprint
# pip install lxml
# pip install beautifulsoup4
from bs4 import BeautifulSoup

from async_parse_tools import AsyncRequests, ClientSession

urls = tuple(f'https://jsonplaceholder.typicode.com/todos/{x}' for x in range(1,4))


async def parse(url: str, r: bytes, session: ClientSession):
    js = json.loads(r)
    return js


out = (AsyncRequests(connections_limit=5)
       .error_settings(max_tries=2)
       # .set_user_agent()
       # .set_cookies()
       # .set_headers()
       .run(urls, parse))

pprint(out)


async def as_completed():
    ar = AsyncRequests(connections_limit=5).error_settings(max_tries=2)
    out = []
    async for x in ar.run_async_as_completed(urls, parse):
        out.append(x)
    pprint(out)


asyncio.run(as_completed())