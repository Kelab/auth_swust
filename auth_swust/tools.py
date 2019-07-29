import time


def retry(times=3, second=0.3):  # 默认重试间隔为0.3秒，重试次数为3次
    def decorator(func):
        def wrapper(*args, **kwargs):
            i = 0
            result = func(*args, **kwargs)
            while not result and i < times:
                print(f"retry {i + 1} times")
                time.sleep(second)
                i += 1
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


def encrypt(plaintext_text, public_modulus_hex, public_exponent_hex):
    """
    Same output with the JS RSA encryptString function on http://www.ohdave.com/rsa/
    Links: https://github.com/icemage001/10086/blob/dbe157b1a0cd9a7c9c0eee517abdbd7ee35072d9/RSA.py
    """
    public_modulus = int(public_modulus_hex, 16)
    public_exponent = int(public_exponent_hex, 16)
    # Beware, plaintext must be short enough to fit in a single block!
    plaintext = int(plaintext_text[::-1].encode("utf-8").hex(), 16)
    ciphertext = pow(plaintext, public_exponent, public_modulus)
    return '%x' % ciphertext  # return hex representation
