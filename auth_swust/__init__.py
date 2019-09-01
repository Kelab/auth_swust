"""
auth_swust
------------------

使用 Python 写成的模拟登录教务处的包。
usage:

   >>> from auth_swust import Login
   >>> login = Login("xxxxxx", "xxxxxxx")
   >>> res = login.try_login()
   >>> res.text
   {"success":true,"code":"10000","msg":"成功","sub_code":"SUCCESS"...

... 或者你可以开启 debug 模式，看看每一步发生了什么:

   >>> Login("xxxxx", "xxxxxx", debug=True)
   >>> res = login.try_login()
   get_init_sess
   get_cap
   cap_code： None
   get_cap
   cap_code： 21YE
   get_auth_sess
   encrypted_pw： xxxxxxx
   <RequestsCookieJar[xxxxx
"""
from .auth_ import Login
from .captcha_recognition import predict_captcha

__all__ = ["Login", "predict_captcha"]
