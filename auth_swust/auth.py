import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests

from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from typing import Tuple, Union, Any
from requests import Response, RequestException
from collections import defaultdict

from .log import AUTH_LOGGER
from .tools import encrypt, retry, meta_redirect
from .typing import CaptchaFailError, AuthFailError
from .headers import get_one
from .constants import URL
from .captcha_recognition import predict_captcha


class Login:
    """登录模块
    以下 raise 的错误都不会影响用户层面，用户层面关心 try_login() 的返回值即可

    :raises ValueError: 登录过程中手动引起 error，使程序重跑\n
    :raises AuthFailError: 用户名或密码错误\n
    :raises CaptchaFailError: 验证码无效
    """
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
            AUTH_LOGGER.debug("跟随页面重定向:{}".format(url))
            response = self.sess.get(url, **kwargs)
            redirected, url = meta_redirect(response.text)

        return response

    def auth_redirections_hooks(self, response: Response, *args, **kwargs):
        redirected, url = meta_redirect(response.text)

        while redirected:
            AUTH_LOGGER.debug("跟随页面重定向:{}".format(url))
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
    def try_login(self) -> Union[Tuple[bool, str], Tuple[bool, Any]]:
        """尝试登录
        因为装饰器的缘故，真正的返回内容在装饰器中。

        :return: 返回的是一个 tuple 元组

        登录失败 -> 返回 (False, 失败原因)。
            失败原因:
                - NormalFail： 重试五次失败或者其他原因。正常的未登录成功
                - AuthFail：用户名或密码错误。
                - RequestException：请求错误，可能是教务处的网站错误或者是本地网络的问题。

        登录成功 -> 返回 (True, 个人信息); 个人信息是一个 Response 对象
        """

        try:
            # 在这些函数内部有 raise 产生错误来中断程序运行
            # 在外层可以捕捉到并进行处理
            self.get_init_sess()
            self.get_cap()
            self.parse_hidden()
            self.get_encrypt_key()
            self.get_auth_sess()
            self.add_server_cookie()
            return self.check_success()
        except AuthFailError:
            return False, "AuthFail"
        except RequestException:
            return False, "RequestException"
        except Exception as e:
            AUTH_LOGGER.debug("Exception: {}".format(e))
            return False, "NormalFail"

    def get_init_sess(self):
        self.sess.headers = get_one()
        self.init_response: Response = self.sess.get(URL.index_url,
                                                     timeout=3,
                                                     hooks=self.hooks("get"))

        AUTH_LOGGER.debug('初始化')

    def get_cap(self):
        _count = 1
        cap_code = None
        while cap_code is None:
            AUTH_LOGGER.debug('获取验证码图片')
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
                cap_code = predict_captcha(im)

            AUTH_LOGGER.debug('识别出验证码：{}'.format(cap_code))

            _count = _count + 1
            if _count > 5:
                AUTH_LOGGER.error('五次获取验证码失败')
                raise ValueError("五次获取验证码失败")

        self.cap_code = cap_code

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
        key_resp = self.sess.get(URL.get_key_url)
        key_dict: dict = key_resp.json()

        modulus = key_dict.get('modulus')
        public_exponent = key_dict.get('exponent')

        # 逆序
        pw_re = self.password[::-1]
        _encrypted_pw = encrypt(modulus, public_exponent)(pw_re)
        self.encrypted_pw = _encrypted_pw
        AUTH_LOGGER.debug('加密密码：{}'.format(_encrypted_pw))

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

        AUTH_LOGGER.debug('登录信息: {}'.format(post_data))
        AUTH_LOGGER.debug('正在发送登录信息...')
        # 登录请求
        resp = self.sess.post(URL.index_url,
                              data=post_data,
                              timeout=3,
                              headers={"Content-Language": "zh-CN"},
                              hooks=self.hooks("auth"))
        soup = BeautifulSoup(resp.text, features="lxml")
        login_form = soup.select("#fm1")
        if len(login_form) != 0:
            error_info = soup.select_one("#fm1 > ul > li.simLi > p > b")
            if error_info:
                if error_info.string == "Invalid credentials.":
                    AUTH_LOGGER.error("用户名或密码错误")
                    raise AuthFailError()
                elif error_info.string == "authenticationFailure.CaptchaFailException":
                    AUTH_LOGGER.debug("当前验证码无效")
                    raise CaptchaFailError()
                else:
                    AUTH_LOGGER.debug("检测到错误: {}".format(error_info.string))

    # 检查是否登陆成功
    def check_success(self):
        # 请求个人信息
        resp: Response = self.sess.get(URL.student_info_url,
                                       verify=False,
                                       allow_redirects=True,
                                       hooks=self.hooks("get"))

        # 试试获取到的是不是 json 数据：
        # 1. 获取到的不是 json 数据的话执行 json() 方法会报错
        # 2. 登录成功，成功获取到 json 格式的个人信息
        try:
            resp.json()
        except Exception:
            AUTH_LOGGER.debug('登录失败！未获取到个人信息。')
            raise ValueError("登录失败！未获取到个人信息。")
        else:
            # 没报错就会执行到这儿
            AUTH_LOGGER.debug('登录成功。')
            return True, resp

    def get_cookies(self):
        return self.sess.cookies

    def get_cookie_jar_obj(self):
        AUTH_LOGGER.warn("deprecated: 请使用 get_cookies() 方法。")
        return self.get_cookies()

    def add_server_cookie(self):
        AUTH_LOGGER.debug("正在登录验证常用教务网站。")
        self.sess.get(URL.jwc_auth_url, verify=False, hooks=self.hooks("get"))
        self.sess.get(URL.syk_auth_url, verify=False, hooks=self.hooks("get"))
