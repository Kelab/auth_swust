import unittest
from pathlib import Path
from auth_swust import predict_captcha
from PIL import Image

captcha_folder = Path(__file__).parent.joinpath('assets', 'captcha')


class TestEvent(unittest.TestCase):
    def test_captcha1(self):
        # 使用绝对路径 设置model的位置
        captcha_path = str(captcha_folder.joinpath('captcha1.jpg'))
        img = Image.open(captcha_path)
        code = predict_captcha(img)
        print(code)
        assert code == "EEL1"

    def test_captcha2(self):
        # 使用绝对路径 设置model的位置
        captcha_path = str(captcha_folder.joinpath('captcha2.jpg'))
        img = Image.open(captcha_path)
        code = predict_captcha(img)
        print(code)
        assert code == "B5FI"

    def test_captcha3(self):
        # 使用绝对路径 设置model的位置
        captcha_path = str(captcha_folder.joinpath('captcha3.jpg'))
        img = Image.open(captcha_path)
        code = predict_captcha(img)
        print(code)
        assert code == "ZDSM"

    def test_captcha4(self):
        # 使用绝对路径 设置model的位置
        captcha_path = str(captcha_folder.joinpath('captcha4.jpg'))
        img = Image.open(captcha_path)
        code = predict_captcha(img)
        print(code)
        assert code == "ZU59"
