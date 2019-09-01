import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests

from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from requests import Response, ConnectionError
from collections import defaultdict

from .tools import encrypt, retry, meta_redirect
from .headers import get_one
from .constants import URL
from .captcha_recognition import predict_captcha
from .log import AuthLogger


class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        _sess = requests.Session()
        self.sess = _sess

        self.init_response = None
        self.cap_code = None
        self.post_data = None
        self.hidden_values = defaultdict(str)

    def get_redirections_hooks(self, response: Response, *args, **kwargs):
        redirected, url = meta_redirect(response.text)

        while redirected:
            AuthLogger.debug("get hooks: redirected url:{}".format(url))
            response = self.sess.get(url, **kwargs)
            redirected, url = meta_redirect(response.text)

        return response

    def auth_redirections_hooks(self, response: Response, *args, **kwargs):
        redirected, url = meta_redirect(response.text)

        while redirected:
            AuthLogger.debug("post hooks: redirected url:{}".format(url))
            response = self.sess.post(URL.index_url,
                                      data=self.post_data,
                                      **kwargs)
            redirected, url = meta_redirect(response.text)

        return response

    def hooks(self, tp="get"):
        if tp == "get":
            return {'response': self.get_redirections_hooks}
        elif tp == "auth":
            return {'response': self.auth_redirections_hooks}
        else:
            return {}

    @retry(times=5, second=1)
    def try_login(self):
        try:
            self.get_init_sess()
            self.get_cap()
            self.parse_hidden()
            self.get_encrypt_key()
            self.get_auth_sess()
            self.add_server_cookie()
            return self.check_success()
        except Exception as e:
            AuthLogger.debug("try_login Exception: {}".format(e))
            return False

    def get_init_sess(self):
        self.sess.headers = get_one()
        self.init_response: Response = self.sess.get(URL.index_url,
                                                     timeout=3,
                                                     hooks=self.hooks("get"))

        AuthLogger.debug('get_init_sess')

    def get_cap(self):
        _count = 1
        while self.cap_code is None:
            AuthLogger.debug('start get_cap')
            im = None
            try:
                cap = self.sess.get(URL.captcha_url,
                                    timeout=3,
                                    hooks=self.hooks("get"))
                imgBuf = BytesIO(cap.content)
                im: Image.Image = Image.open(imgBuf)
            except Exception:
                continue

            # 验证码识别
            if im is not None:
                # 返回字符或者 None
                code = predict_captcha(im)
                self.cap_code = code

            AuthLogger.debug('cap_code：{}'.format(self.cap_code))

            _count = _count + 1
            if _count > 5:
                AuthLogger.error('五次获取验证码失败')
                break

    def parse_hidden(self):
        """
        解析 post 需要的参数
        <input name="execution" type="hidden" value="e1s1"/>,
        <input name="_eventId" type="hidden" value="submit"/>,
        <input name="geolocation" type="hidden"/>
        """
        bs = BeautifulSoup(self.init_response.text, "lxml")
        _execution = bs.select_one('#fm1 > ul input[name="execution"]')
        _eventId = bs.select_one('#fm1 > ul input[name="_eventId"]')

        if _execution is not None:
            self.hidden_values['execution'] = _execution.attrs['value']
            self.hidden_values['_eventId'] = _eventId.attrs['value']
            # 可以不用对 hidden_values['geolocation'] 赋值

    def get_encrypt_key(self):
        try:
            key_resp = self.sess.get(URL.get_key_url)
            key_dict: dict = key_resp.json()
        except ConnectionError:
            AuthLogger.debug('key server return:'.format(key_resp.text[:1000]))
            raise ValueError("无法获取加密 key")

        modulus = key_dict.get('modulus')
        public_exponent = key_dict.get('exponent')

        # 逆序
        pw_re = self.password[::-1]
        _encrypted_pw = encrypt(modulus, public_exponent)(pw_re)
        self.encrypted_pw = _encrypted_pw
        AuthLogger.debug('encrypted password：{}'.format(_encrypted_pw))

    def get_auth_sess(self):
        post_data = {
            "username": self.username,
            "password": self.encrypted_pw,
            "captcha": self.cap_code,
            "execution": self.hidden_values['execution'],
            "_eventId": self.hidden_values['_eventId'],
            "geolocation": self.hidden_values['geolocation']
        }
        self.post_data = post_data

        resp = self.sess.post(URL.index_url,
                              data=post_data,
                              timeout=3,
                              hooks=self.hooks("auth"))

        AuthLogger.debug('post_data: {}'.format(post_data))
        AuthLogger.debug('get_auth_sess: {}'.format(resp.text[:1000]))

    # 检查是否登陆成功
    def check_success(self):
        # 请求个人信息
        res = self.sess.get(URL.student_info_url,
                            verify=False,
                            allow_redirects=True,
                            hooks=self.hooks("get"))

        AuthLogger.debug("验证是否登录: {}".format(res.text[:100]))

        # 一般就是两种可能：
        # 1. 没登录成功，302 跳到 cas.swust 页面，这时候执行 json() 方法会报错
        # 2. 登录成功，成功获取到 json 格式的个人信息
        try:
            res.json()
        except Exception:
            AuthLogger.debug('login failed')
            return False
        else:
            # 没报错就会执行到这儿
            AuthLogger.debug('login success')
            return res

    def get_cookies(self):
        return self.sess.cookies

    def get_cookie_jar_obj(self):
        AuthLogger.warn("deprecated: 请使用 get_cookies() 方法。")
        return self.get_cookies()

    def add_server_cookie(self):
        self.sess.get(URL.jwc_auth_url, verify=False, hooks=self.hooks("get"))
        self.sess.get(URL.syk_auth_url, verify=False, hooks=self.hooks("get"))

        AuthLogger.debug("self.sess.cookies {}".format(self.sess.cookies))
