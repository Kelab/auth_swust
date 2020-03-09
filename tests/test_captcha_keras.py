import os

os.environ["CAPTCHA_BACKEND"] = "keras"
from pathlib import Path
from auth_swust import predict_captcha
from PIL import Image

# 使用绝对路径 设置model的位置
captcha_folder = Path(__file__).parent.joinpath("assets", "captcha")


class TestCaptcha:
    def test_captcha1(self):
        captcha_path = str(captcha_folder.joinpath("1DXH.jpg"))
        img = Image.open(captcha_path)
        code = predict_captcha(img)
        print(code)
        assert code == "1DXH"

    def test_captcha2(self):
        captcha_path = str(captcha_folder.joinpath("RZSL.jpg"))
        img = Image.open(captcha_path)
        code = predict_captcha(img)
        print(code)
        assert code == "RZSL"
