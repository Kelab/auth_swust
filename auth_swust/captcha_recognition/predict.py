import os
import string

import numpy as np
import tensorflow as tf
from keras.models import load_model

from .img_process import process
from .segment import segment_image

# 设置model的位置
path = os.path.split(os.path.realpath(__file__))[0]
model_path = os.path.join(path, r'model\captcha_cnn.model')

# 加载模型
model = load_model(model_path)

global graph
graph = tf.get_default_graph()


def decode(v):
    s = ''
    str = string.digits + string.ascii_uppercase
    for x in v:
        s += str[int(x.argmax())]
    return s


def predict_captcha(captcha_image):
    """
    :param captcha_image: captcha image path
    :return: str 验证码
    """
    # segment_iamge 抽取小图像
    image = process(captcha_image)

    subimages = segment_image(image)
    if subimages is not None:
        dataset = np.array(subimages)
        with graph.as_default():
            predicted_word = decode(model.predict(dataset.reshape((4, 1, 32, 32))))
        return predicted_word

    # segment_iamge 抽取小图像
    image = process(captcha_image, 3)

    subimages = segment_image(image)
    if subimages is not None:
        dataset = np.array(subimages)
        with graph.as_default():
            predicted_word = decode(model.predict(dataset.reshape((4, 1, 32, 32))))
        return predicted_word

    # 如果切割图片返回None 说明没有切割出来 直接不预测
    return None


label_list = list(string.digits + string.ascii_uppercase)
