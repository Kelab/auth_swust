from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from typing import Tuple, Union, Any
from requests import Response, RequestException, ReadTimeout
from collections import defaultdict

from .log import AuthLogger
from .tools import encrypt, retry
from .request import Session
from .headers import get_headers
from .constants import URL
from .exceptions import CaptchaFailError, AuthFailError
from .captcha_recognition import predict_captcha


class Login:
    """登录模块
    登录核心模块


    :raises ValueError: 登录过程中手动引起 error，使程序重跑\n
    :raises AuthFailError: 用户名或密码错误\n
    :raises CaptchaFailError: 验证码无效
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.sess = Session()
        self.sess.headers = get_headers()

        self.init_resp = None
        self.cap_code = None
        self.hidden_values = defaultdict(str)

    @retry(times=5, second=1)
    def try_login(self) -> Union[Tuple[bool, str], Tuple[bool, Any]]:
        """尝试登录
        因为装饰器的缘故，真正的返回内容在装饰器中：。

        :return: 返回的是一个 tuple 元组：(result, info)

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
            self.init()
            self.auth()
        except AuthFailError:
            return False, "AuthFail"
        except ReadTimeout as e:
            AuthLogger.error("❌ 请求超时: {}".format(e))
            return self.check_success()
        except RequestException as e:
            AuthLogger.error("❌ 请求错误，可能是教务处的网站错误或者是本地网络的问题。: {}".format(e))
            return False, "RequestException"
        except Exception as e:
            AuthLogger.error("❌ 捕获到异常: {}".format(e))
            return False, "NormalFail"
        else:
            return self.check_success()

    def init(self):
        try:

            AuthLogger.debug('正在初始化...')
            self.init_resp: Response = self.sess.get(URL.index_url, timeout=8)
            self.parse_auth_params()
            self.encrypt_password()
            self.get_captcha_code()
            AuthLogger.debug('✔ 初始化完成')

        except ReadTimeout:
            raise RequestException("初始化加载网页信息超时")

    def get_captcha_code(self):
        _count = 0
        cap_code = None
        while cap_code is None and _count < 5:
            AuthLogger.debug('正在获取验证码图片...')
            cap = self.sess.get(URL.captcha_url, timeout=3)
            img_buffer = BytesIO(cap.content)
            with Image.open(img_buffer) as im:
                # 验证码识别
                if im is not None:
                    # 返回字符或者 None
                    cap_code = predict_captcha(im)

            AuthLogger.debug('识别验证码结果：{}'.format(cap_code))

            _count = _count + 1

        if cap_code:
            AuthLogger.debug('✔ 识别验证码成功')
            self.cap_code = cap_code
        else:
            raise ValueError("获取验证码失败")

    def parse_auth_params(self):
        """
        解析 post 需要的参数
        <input name="execution" type="hidden" value="e1s1"/>,
        <input name="_eventId" type="hidden" value="submit"/>,
        <input name="geolocation" type="hidden"/>
        """
        bs = BeautifulSoup(self.init_resp.text, "lxml")
        _execution = bs.select_one('#fm1 > ul input[name="execution"]')
        _eventId = bs.select_one('#fm1 > ul input[name="_eventId"]')

        if _execution:
            self.hidden_values['execution'] = _execution.attrs['value']
            self.hidden_values['_eventId'] = _eventId.attrs['value']

    def encrypt_password(self):
        AuthLogger.debug('正在加密密码...')
        key_resp = self.sess.get(URL.get_key_url)
        key_dict: dict = key_resp.json()

        modulus = key_dict.get('modulus')
        public_exponent = key_dict.get('exponent')

        # 逆序
        pw_re = self.password[::-1]
        encrypted_pw = encrypt(modulus, public_exponent)(pw_re)
        self.encrypted_pw = encrypted_pw
        AuthLogger.debug('✔ 加密密码成功。')

    def auth(self):
        post_data = {
            "username": self.username,
            "password": self.encrypted_pw,
            "captcha": self.cap_code,
            "execution": self.hidden_values['execution'],
            "_eventId": self.hidden_values['_eventId'],
            "geolocation": self.hidden_values['geolocation']
        }

        AuthLogger.debug('正在发送登录信息: {}'.format(post_data))
        # 登录请求
        resp = self.sess.post(
            URL.index_url,
            data=post_data,
            timeout=10,
        )
        soup = BeautifulSoup(resp.text, "lxml")

        # 获取错误信息
        error_info = soup.select_one("#fm1 > ul > li.simLi > p > b")
        if error_info:
            if error_info.string == "Invalid credentials.":
                AuthLogger.error("用户名或密码错误")
                raise AuthFailError("用户名或密码错误")
            elif error_info.string == "authenticationFailure.CaptchaFailException":
                AuthLogger.error("验证码无效")
                raise CaptchaFailError("验证码无效")

    # 检查是否登陆成功
    def check_success(self):
        # 请求个人信息 expect: json格式的个人信息
        resp: Response = self.sess.get(URL.student_info_url,
                                       verify=False,
                                       allow_redirects=True)

        # 试试获取到的是不是 json 数据：
        # 1. 获取到的不是 json 数据的话执行 json() 方法会报错
        # 2. 登录成功，成功获取到 json 格式的个人信息
        try:
            resp.json()
        except Exception:
            AuthLogger.error('登录失败！未获取到个人信息。')
            return False, 'NormalFail'
        else:
            AuthLogger.info('登录成功。')
            self.add_common_website_cookies()
            self.sess.close()
            return True, resp

    def get_cookies(self):
        return self.sess.cookies

    def get_cookie_jar_obj(self):
        AuthLogger.warn("deprecated: 请使用 get_cookies() 方法。")
        return self.get_cookies()

    def add_common_website_cookies(self):
        AuthLogger.debug("正在登录验证常用教务网站。")
        self.sess.get(URL.jwc_auth_url, verify=False)
        self.sess.get(URL.syk_auth_url, verify=False)
