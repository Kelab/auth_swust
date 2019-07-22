import os
from io import BytesIO

import requests
from PIL import Image
from bs4 import BeautifulSoup
from requests import ConnectionError
from requests.cookies import RequestsCookieJar

from .captcha_recognition import predict_captcha
from .constants import URL
from .headers import get_one
from .tools import encrypt
from .tools import retry


class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        _sess = requests.session()
        _sess.headers = get_one()
        self.sess = _sess

        self.cap_code = None
        self.post_data = None
        self.res = None
        self.key_dict = None

        self.execution_value = ""
        self._eventId_value = ""
        self.geolocation_value = ""

    def get_init_sess(self, url):
        self.res = self.sess.get(url)

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

        cookie_jar = RequestsCookieJar()
        cookie_jar.set("remember", "true", expires=7)
        cookie_jar.set("username", self.username, expires=7)
        cookie_jar.set("password", self.password, expires=7)


        self.sess.post(URL.index_url, data=self.post_data, headers=get_one())

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
        self.execution_value = execution_.attrs['value']
        self._eventId_value = _eventId_.attrs['value']

        try:
            self.geolocation_value = geolocation_.attrs['value']
        except KeyError:
            self.geolocation_value = ""

    def get_cap(self):
        cap = self.sess.get(URL.captcha_url)
        imgBuf = BytesIO(cap.content)
        flag = True
        while flag is True:
            try:
                cap = self.sess.get(URL.captcha_url)
                imgBuf = BytesIO(cap.content)
                im = Image.open(imgBuf)
            except Exception:
                pass
            else:
                flag = False

        # 验证码识别
        code = predict_captcha(im)
        if code:
            self.cap_code = code
        else:
            self.cap_code = 'xxxx'

    # 检查是否登陆成功
    def check_success(self):
        # 如果有 302 跳转，说明没登录
        res = self.sess.get(URL.student_info_url, allow_redirects=False)
        try:
            res.json()
        except:
            flag = False
        else:
            flag = True
        if res.status_code == 302 or not flag:
            return False
        else:
            return res

    @retry(times=3, second=0.3)
    def try_login(self):
        self.get_init_sess(URL.index_url)
        self.get_cap()
        self.parse_hidden()
        self.get_encrypt_key()
        self.get_auth_sess()
        return self.check_success()

    def get_cookie_jar_obj(self):
        return self.sess.cookies
