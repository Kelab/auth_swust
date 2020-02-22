import os
import sys

from PIL import Image
from loguru import logger

from .img_process import process
from .segment import segment_image

_BACKEND = "pytorch"
_BACKEND = os.environ.get("CAPTCHA_BACKEND", _BACKEND)

if _BACKEND == "keras":
    logger.info("使用 Keras 进行验证码识别。")
    from .keras_backend import _predict
else:
    logger.info("使用 Pytorch 进行验证码识别。")
    from .torch_backend import _predict


def predict_captcha(captcha_image: Image.Image):
    """
    :param captcha_image: captcha image path
    :return: str 验证码
    """
    # segment_iamge 抽取小图像，降噪指数默认 2
    image = process(captcha_image)
    subimages = segment_image(image)

    if subimages is not None:
        return _predict(subimages)

    # 如果切割图片返回 None 说明没有切割出来 直接不预测
    return None
