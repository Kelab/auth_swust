import requests
from requests.adapters import HTTPAdapter
from requests.structures import CaseInsensitiveDict


def ajax_auth_server(sess: requests.Session,
                     url: str,
                     method: str = 'GET',
                     **kwargs):
    r"""向 `cas.swust.edu.cn` 发请求. 返回 :class:`Response` 对象.

    :param sess: 传入要发请求的 sess
    :param method: GET 还是 POST
    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """
    print("ajax_auth_server", url)
    # headers = {'Host': 'cas.swust.edu.cn'}
    return sess.request(method.upper(), url, **kwargs)


class AuthAdapter(HTTPAdapter):
    def add_headers(self, request: requests.PreparedRequest, **kwargs):
        print('add_headers -> cookies', request.headers.get('Cookie'))

        request.headers.update({'Host': "cas.swust.edu.cn"})
        print(request.url)
