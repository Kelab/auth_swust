import re
from collections import defaultdict
from io import BytesIO
from typing import Any, Tuple, Union

from bs4 import BeautifulSoup
from loguru import logger
from PIL import Image
from requests import ReadTimeout, RequestException, Response

from .captcha_recognition import predict_captcha
from .constants import URL
from .exceptions import AuthFailError, CaptchaFailError
from .helpers.request import get_random_ua, Session
from .helpers.utils import encrypt, retry


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

        self.login_other = None
        self.init_resp = None
        self.cap_code = None
        self.hidden_values = defaultdict(str)

    @retry(times=5, second=0.3)
    def try_login(
            self,
            login_other=True) -> Union[Tuple[bool, str], Tuple[bool, Any]]:
        """尝试登录
        参数：login_other: bool 是否顺带登录教务处和实验课的网站以获取相应 cookie

        因为装饰器的缘故，真正的返回内容在装饰器中：。

        :return: 返回的是一个 tuple 元组：(result, info)

        登录失败 -> 返回 (False, 失败原因)。
            失败原因:
                - NormalFail： 重试五次失败或者其他原因。正常的未登录成功
                - AuthFail：用户名或密码错误。
                - RequestException：请求错误，可能是教务处的网站错误或者是本地网络的问题。

        登录成功 -> 返回 (True, 个人信息); 个人信息是一个 Response 对象
        """
        self.login_other = login_other
        try:
            # 在这些函数内部有 raise 产生错误来中断程序运行
            # 在外层可以捕捉到并进行处理
            self.init()
            self.auth()
        except AuthFailError:
            return False, "AuthFail"
        except ReadTimeout as e:
            logger.error("❌ 请求超时: {}".format(e))
            return self.check_success()
        except RequestException as e:
            logger.error("❌ 网络错误，可能是教务处的网站错误或者是本地网络的问题。: {}".format(e))
            return False, "RequestException"
        except Exception as e:
            logger.error("❌ 捕获到异常: {}".format(e))
            return False, "NormalFail"
        else:
            return self.check_success()

    def init(self):
        try:
            logger.debug("正在初始化...")
            sess = Session()
            sess.headers = get_random_ua()
            sess.verify = False
            self.sess = sess
            self.init_resp: Response = self.sess.get(URL.index_url, timeout=8)
            self.parse_auth_params()
            self.encrypt_password()
            self.get_captcha_code()
            logger.debug("✔ 初始化完成")

        except ReadTimeout:
            raise RequestException("初始化加载网页信息超时")

    def get_captcha_code(self):
        _count = 0
        cap_code = None
        while cap_code is None and _count < 5:
            logger.debug("正在获取验证码图片...")
            cap = self.sess.get(URL.captcha_url, timeout=3)
            img_buffer = BytesIO(cap.content)
            with Image.open(img_buffer) as im:
                # 验证码识别
                if im is not None:
                    # 返回字符或者 None
                    cap_code = predict_captcha(im)

            logger.debug("识别验证码结果：{}".format(cap_code))

            _count = _count + 1

        if cap_code:
            logger.debug("✔ 识别验证码")
            self.cap_code = cap_code
        else:
            raise ValueError("识别验证码失败")

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
            self.hidden_values["execution"] = _execution.attrs["value"]
            self.hidden_values["_eventId"] = _eventId.attrs["value"]

    def encrypt_password(self):
        logger.debug("正在加密密码...")
        key_resp = self.sess.get(URL.get_key_url)
        key_dict: dict = key_resp.json()

        modulus = key_dict.get("modulus")
        public_exponent = key_dict.get("exponent")

        # 逆序
        pw_re = self.password[::-1]
        encrypted_pw = encrypt(modulus, public_exponent)(pw_re)
        self.encrypted_pw = encrypted_pw
        logger.debug("✔ 加密密码成功。")

    def auth(self):
        post_data = {
            "username": self.username,
            "password": self.encrypted_pw,
            "captcha": self.cap_code,
            "execution": self.hidden_values["execution"],
            "_eventId": self.hidden_values["_eventId"],
            "geolocation": self.hidden_values["geolocation"],
        }

        logger.debug("正在发送登录信息: {}".format(post_data))
        # 登录请求
        resp = self.sess.post(URL.index_url, data=post_data, timeout=5)
        soup = BeautifulSoup(resp.text, "lxml")

        # 获取错误信息
        error_info = soup.select_one("#fm1 > ul > li.simLi > p > b")
        if error_info:
            if error_info.string == "Invalid credentials.":
                logger.error("❌ 用户名或密码错误")
                raise AuthFailError("用户名或密码错误")
            elif error_info.string == "authenticationFailure.CaptchaFailException":
                logger.error("❌ 验证码无效")
                raise CaptchaFailError("验证码无效")

    # 检查是否登陆成功
    def check_success(self):
        # 请求个人信息 expect: json格式的个人信息
        resp: Response = self.sess.get(URL.student_info_url,
                                       allow_redirects=True)

        # 试试获取到的是不是 json 数据：
        # 1. 获取到的不是 json 数据的话执行 json() 方法会报错
        # 2. 登录成功，成功获取到 json 格式的个人信息
        try:
            resp.json()
        except Exception:
            logger.error("❌ 登录失败！未获取到个人信息。")
            return False, "NormalFail"
        else:
            logger.info("登录成功。")
            if self.login_other:
                self.add_common_website_cookies()
            self.sess.close()
            return True, resp

    def get_cookies(self):
        return self.sess.cookies

    def add_common_website_cookies(self):
        logger.debug("正在登录验证常用教务网站。")
        try:
            self.sess.get(URL.jwc_auth_url)

            verify = self.sess.get(URL.syk_auth_url)
            soup = BeautifulSoup(verify.text, "lxml")
            script = soup.find("script")
            if script:
                string = script.string
                c = re.compile(r"window\.location='(.+)';")
                location = c.match(string)
                verify_href = location.group(1)
                self.sess.get(URL.syk_base_url + verify_href)
                self.sess.get(URL.syk_base_url + "/StuExpbook/login.jsp")
            else:
                logger.error("❌ 登录实验课网站失败")
        except Exception:
            logger.debug("❌ 登录验证常用教务网站失败。")
        else:
            logger.debug("✔ 登录验证常用教务网站成功。")
