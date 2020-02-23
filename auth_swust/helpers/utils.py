import time

from loguru import logger


def encrypt(public_modulus_hex, public_exponent_hex):
    """
    Same output with the JS RSA encryptString function on http://www.ohdave.com/rsa/ \n
    Links: https://github.com/icemage001/10086/blob/master/RSA.py
    """
    public_modulus = int(public_modulus_hex, 16)
    public_exponent = int(public_exponent_hex, 16)

    def cipher(text):
        # Beware, plaintext must be short enough to fit in a single block!
        plaintext = int(text[::-1].encode("utf-8").hex(), 16)
        ciphertext = pow(plaintext, public_exponent, public_modulus)
        return "%x" % ciphertext  # return hex representation

    return cipher


def retry(times: int = 3, second: int = 1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            i = 0
            # 设置密码错误重试次数
            auth_fail_count = 0
            result, info = func(*args, **kwargs)
            while not result and i < times:
                logger.debug(f"登录失败，开始重试第 {i + 1} 次")
                time.sleep(second)

                if result is False and info == "AuthFail":
                    auth_fail_count = auth_fail_count + 1
                    if auth_fail_count > 2:
                        # 如果重试密码错误两次，就返回密码错误
                        return result, info

                i += 1
                result, info = func(*args, **kwargs)

            return result, info

        return wrapper

    return decorator
