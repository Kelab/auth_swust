import requests
from requests.adapters import HTTPAdapter


class AuthAdapter(HTTPAdapter):
    def add_headers(self, request: requests.PreparedRequest, **kwargs):
        print('add_headers -> cookies', request.headers.get('Cookie'))

        request.headers.update({'Host': "cas.swust.edu.cn"})
        print(request.url)
