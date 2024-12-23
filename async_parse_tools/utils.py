import json
import os.path
import re
from random import choice
from typing import List, Dict
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/105.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/106.0.0.0 Safari/537.36'
    'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/105.0.0.0 Safari/537.36'
]


def get_random_user_agent() -> str:
    """Возвращает случайный User Agent из списка"""
    return choice([USER_AGENTS])[0]


def convert_cookies_to_dict(cookies: List[Dict]) -> Dict:
    """converting cookies to dictionary. Useful for passing to requests or aiohttp library"""
    return {x['name']: x['value'] for x in cookies}


def load_json_cookies_as_dict(path: str) -> Dict:
    """Loads and converting cookies to dictionary. Useful for passing to requests or aiohttp library"""
    cookies = load_json(path)
    return convert_cookies_to_dict(cookies)


def build_url_with_params(url: str, params: dict):
    url_parsed = urlparse(url)
    query = dict(parse_qsl(url_parsed.query))
    query.update(params)
    url_parsed = url_parsed._replace(query=urlencode(query))
    return urlunparse(url_parsed)


def save_json(path: str, obj, ensure_ascii=False):
    if not os.path.exists(path):
        folder = os.path.split(path)
        if folder[0]:
            try:
                os.makedirs(folder[0])
            except FileExistsError:
                pass
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=4, ensure_ascii=ensure_ascii)


def load_json(path: str):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def remove_forbidden_symbols(line: str):
    symbols = '/\\:\"*?«<>|'
    return ''.join([x for x in line if x not in symbols])


def filter_strip(items: tuple[str] | list[str]):
    seen = set()
    for item in items:
        if item not in seen:
            yield item.strip()
            seen.add(item)


REGEX_URL = r'(?P<host>[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6})\b(?P<path>[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
REGEX_URL_HTTP = r'(?P<protocol>https?):\/\/(?P<www>www\.)?' \
                 r'(?P<host>[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6})\b' \
                 r'(?P<path>[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'


def regex_url(url: str, protocol=True, match=False):
    f = re.match if match else re.findall

    if protocol:
        return f(REGEX_URL_HTTP, url)
    return f(REGEX_URL, url)


parse_url = urlparse
# def parse_url(url):
#     return urlparse(url)


def get_base_url(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}/"
