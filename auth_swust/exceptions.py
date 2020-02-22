class CaptchaFailError(Exception):
    """
    验证码无效
    """

    pass


class AuthFailError(Exception):
    """
    用户名或密码错误
    """

    pass
