import time

from bs4 import BeautifulSoup

from .log import AuthLogger


def retry(times=3, second=1):  # 默认重试间隔为0.3秒，重试次数为3次
    def decorator(func):
        def wrapper(*args, **kwargs):
            i = 0
            result, info = func(*args, **kwargs)
            while not result and i < times:
                if info == "AuthFail":
                    return result, info

                AuthLogger.debug(f"登录失败，开始重试第 {i + 1} 次")
                time.sleep(second)
                i += 1
                result, info = func(*args, **kwargs)
            return result, info

        return wrapper

    return decorator


def encrypt(public_modulus_hex, public_exponent_hex):
    """
    闭包写法
    Same output with the JS RSA encryptString function on http://www.ohdave.com/rsa/ \n
    Links: https://github.com/icemage001/10086/blob/dbe157b1a0cd9a7c9c0eee517abdbd7ee35072d9/RSA.py
    """
    public_modulus = int(public_modulus_hex, 16)
    public_exponent = int(public_exponent_hex, 16)

    def cipher(text):
        # Beware, plaintext must be short enough to fit in a single block!
        plaintext = int(text[::-1].encode("utf-8").hex(), 16)
        ciphertext = pow(plaintext, public_exponent, public_modulus)
        return '%x' % ciphertext  # return hex representation

    return cipher


def meta_redirect(content):
    soup = BeautifulSoup(content, 'lxml')

    result = soup.find("meta", attrs={"http-equiv": "refresh"})
    if result:
        wait, text = result["content"].split(";")
        if text.strip().lower().startswith("url="):
            url = text[4:]
            return True, url
    return False, None
