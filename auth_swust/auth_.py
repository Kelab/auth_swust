import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests

from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from requests import ConnectionError

from .tools import encrypt, retry, meta_redirect
from .headers import get_one
from .constants import URL
from .captcha_recognition import predict_captcha


class Login:
    def __init__(self, username, password, debug=False):
        self.debug = debug
        self.username = username
        self.password = password
        _sess = requests.Session()
        self.sess = _sess

        self.cap_code = None
        self.post_data = None
        self.res = None
        self.key_dict = None

        self.execution_value = ""
        self._eventId_value = ""
        self.geolocation_value = ""

    def get_redirections_hooks(self, response: requests.Response, *args,
                               **kwargs):
        sess = self.sess
        redirected, url = meta_redirect(response.text)
        while redirected:
            print("get hooks: redirected url:", url)
            response = sess.get(url, **kwargs)
            redirected, url = meta_redirect(response.text)
        return response

    def auth_redirections_hooks(self, response: requests.Response, *args,
                                **kwargs):
        sess = self.sess
        redirected, url = meta_redirect(response.text)

        while redirected:
            print("post hooks: redirected url:", url)
            response = sess.post(URL.index_url,
                                 data=self.post_data,
                                 timeout=5,
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

    @retry(times=5, second=0.3)
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
            print("try_login Exception:", e)
            return False

    def get_init_sess(self):
        self.sess.headers = get_one()
        self.res = self.sess.get(URL.index_url, hooks=self.hooks("get"))
        if self.debug:
            print('get_init_sess')

    def get_cap(self):
        while self.cap_code is None:
            if self.debug:
                print('start get_cap')
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

            if self.debug:
                print('cap_code：', self.cap_code)

    def parse_hidden(self):
        """
        解析 post 需要的参数
        """
        bs = BeautifulSoup(self.res.text, "lxml")
        execution_ = bs.select_one('#fm1 > ul input[name="execution"]')
        _eventId_ = bs.select_one('#fm1 > ul input[name="_eventId"]')
        geolocation_ = bs.select_one('#fm1 > ul input[name="geolocation"]')
        if execution_ is not None:
            # <input name="execution" type="hidden" value="e1s1"/>,
            self.execution_value = execution_.attrs['value']
            # <input name="_eventId" type="hidden" value="submit"/>,
            self._eventId_value = _eventId_.attrs['value']
            # <input name="geolocation" type="hidden"/>
            try:
                self.geolocation_value = geolocation_.attrs['value']
            except KeyError:
                self.geolocation_value = ""

    def get_encrypt_key(self):
        try:
            key_resp = self.sess.get(URL.get_key_url)
            key_dict: dict = key_resp.json()
            self.key_dict = key_dict

        except ConnectionError:
            raise ValueError("无法获取加密 key")

    def get_auth_sess(self):
        modulus = self.key_dict['modulus']
        public_exponent = self.key_dict['exponent']

        pw_re = self.password[::-1]
        encrypted_pw = encrypt(pw_re, modulus, public_exponent)

        post_data = {
            "username": self.username,
            "password": encrypted_pw,
            "captcha": self.cap_code,
            "execution": self.execution_value,
            "_eventId": self._eventId_value,
            "geolocation": self.geolocation_value
        }
        self.post_data = post_data

        self.sess.cookies.set("remember",
                              "true",
                              expires=365,
                              domain='cas.swust.edu.cn',
                              path='/')
        self.sess.cookies.set("username",
                              self.username,
                              expires=365,
                              domain='cas.swust.edu.cn',
                              path='/')
        self.sess.cookies.set("password",
                              self.password,
                              expires=365,
                              domain='cas.swust.edu.cn',
                              path='/')

        self.sess.post(URL.index_url,
                       data=self.post_data,
                       timeout=5,
                       hooks=self.hooks("auth"))

        if self.debug:
            print('get_auth_sess')
            print('encrypted_pw：', encrypted_pw)

    # 检查是否登陆成功
    def check_success(self):
        # 如果有 解析不了json说明为False
        res = self.sess.get(URL.student_info_url,
                            verify=False,
                            allow_redirects=True,
                            hooks=self.hooks("get"))
        try:
            # 因为教务处的劫持，也会返回 200，检测一下是否能转为 json
            res.json()
        except Exception:
            flag = False
        else:
            flag = True

        if self.debug:
            print("check_success:", res.text[:1000])

        if not flag:
            if self.debug:
                print('check failed')
            return False
        else:
            if self.debug:
                print('check success')
            return res

    def get_cookie_jar_obj(self):
        return self.sess.cookies

    def add_server_cookie(self):
        self.sess.get(URL.jwc_auth_url, verify=False, hooks=self.hooks("get"))
        self.sess.get(URL.syk_auth_url, verify=False, hooks=self.hooks("get"))
        if self.debug:
            print("self.sess.cookies", self.sess.cookies)
