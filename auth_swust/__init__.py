"""
auth_swust
------------------

模拟登录教务处。
usage:

   >>> from auth_swust import Login
   >>> login = Login("xxxxxx", "xxxxxxx")
   >>> res, info = login.try_login()
   >>> res
   True
   >>> info
   {"success":true,"code":"10000","msg":"成功","sub_code":"SUCCESS"...

... 或者你可以开启 debug 模式，看看每一步发生了什么:
   >>> from auth_swust.log import AuthLogger, DEBUG
   >>> AuthLogger.setLevel(DEBUG)
   >>> Login("xxxxx", "xxxxxx")
   >>> res, info = login.try_login()
   [2019-09-03 12:14:37] [DEBUG] [auth.py:111] [get_init_sess] > 初始化
   [2019-09-03 12:14:37] [DEBUG] [auth.py:117] [get_cap] > 获取验证码图片
   [2019-09-03 12:14:37] [DEBUG] [auth.py:133] [get_cap] > 识别出验证码：RQDW
   ...
"""
from .auth import Login
from .captcha_recognition import predict_captcha
from . import request
__all__ = ["Login", "predict_captcha", "request"]
