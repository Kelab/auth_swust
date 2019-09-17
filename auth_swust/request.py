import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from bs4 import BeautifulSoup
from requests import Response
from requests import Session as _Session

from .log import AuthLogger
from .headers import get_one


def meta_redirect(content):
    soup = BeautifulSoup(content, 'lxml')

    result = soup.find("meta", attrs={"http-equiv": "refresh"})
    if result:
        wait, text = result["content"].split(";")
        text = text.strip()
        if text.lower().startswith("url="):
            url = text[4:]
            return True, url
    return False, None


class Session(_Session):
    def __init__(self, cookies: dict = {}):
        super().__init__()
        self.cookies.update(cookies)
        self.headers.update(get_one())

    def get_redirections_hooks(self, response: Response, *args, **kwargs):
        redirected, url = meta_redirect(response.text)
        while redirected:
            AuthLogger.debug("跟随页面重定向:{}".format(url))
            response = self.get(url, hooks={}, **kwargs)
            redirected, url = meta_redirect(response.text)

        return response

    def get(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        if 'swust' in url:
            kwargs.setdefault('hooks',
                              {'response': self.get_redirections_hooks})
        return self.request(
            'GET',
            url,
            **kwargs,
        )
