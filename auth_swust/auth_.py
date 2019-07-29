from io import BytesIO

import requests
import urllib3
from PIL import Image
from bs4 import BeautifulSoup
from requests import ConnectionError

from .captcha_recognition import predict_captcha
from .constants import URL
from .headers import get_one
from .tools import encrypt, retry

urllib3.disable_warnings()


class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        _sess = requests.session()
        self.sess = _sess

        self.cap_code = None
        self.post_data = None
        self.res = None
        self.key_dict = None

        self.execution_value = ""
        self._eventId_value = ""
        self.geolocation_value = ""


    def get_init_sess(self):
        self.sess.headers = get_one()
        self.res = self.sess.get(URL.index_url)

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

        self.sess.cookies.set("remember", "true", expires=7)
        self.sess.cookies.set("username", self.username, expires=7)
        self.sess.cookies.set("password", self.password, expires=7)

        self.sess.post(URL.index_url, data=self.post_data, timeout=5)

    def parse_hidden(self):
        """
        <input name="execution" type="hidden" value="e1s1"/>,
        <input name="_eventId" type="hidden" value="submit"/>,
        <input name="geolocation" type="hidden"/>
        """
        bs = BeautifulSoup(self.res.text, "lxml")
        execution_ = bs.select_one('#fm1 > ul input[name="execution"]')
        _eventId_ = bs.select_one('#fm1 > ul input[name="_eventId"]')
        geolocation_ = bs.select_one('#fm1 > ul input[name="geolocation"]')
        if execution_ is not None:
            self.execution_value = execution_.attrs['value']
            self._eventId_value = _eventId_.attrs['value']

            try:
                # 防止以后学校再增加此字段
                self.geolocation_value = geolocation_.attrs['value']
            except KeyError:
                self.geolocation_value = ""

    def get_cap(self):
        im = None
        flag = True
        # 有时候获取不到验证码，那就重新请求验证码
        while flag is True:
            try:
                cap = self.sess.get(URL.captcha_url, timeout=3)
                imgBuf = BytesIO(cap.content)
                im = Image.open(imgBuf)
            except requests.ConnectTimeout:
                flag = False
            except Exception:
                pass
            else:
                flag = False

        # 验证码识别
        if im is not None:
            code = predict_captcha(im)
            if code:
                self.cap_code = code
            else:
                self.cap_code = ''

    # 检查是否登陆成功
    def check_success(self):
        # 如果有 解析不了json说明为False
        res = self.sess.get(URL.student_info_url, allow_redirects=True)
        try:
            # 因为教务处的劫持，也会返回 200，检测一下是否能转为 json
            res.json()
        except Exception:
            flag = False
        else:
            flag = True

        if not flag:
            return False
        else:
            return res

    @retry(times=5, second=0.3)
    def try_login(self):
        try:
            self.get_init_sess()
            self.get_cap()
            self.parse_hidden()
            self.get_encrypt_key()
            self.get_auth_sess()
            return self.check_success()
        except Exception as e:
            print("try_login", e)
            return False

    def get_cookie_jar_obj(self):
        self.add_server_cookie()

        return self.sess.cookies

    def add_server_cookie(self):
        self.sess.get(URL.jwc_auth_url, verify=False)
