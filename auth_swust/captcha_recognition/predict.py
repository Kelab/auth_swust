import os
import string
import numpy as np
import tensorflow as tf
from keras.models import load_model

from .img_process import process
from .segment import segment_image

# 使用绝对路径 设置model的位置
path = os.path.split(os.path.realpath(__file__))[0]
model_path = os.path.join(path, r'model\captcha_cnn.model')

# 加载模型
model = load_model(model_path)

global graph
graph = tf.get_default_graph()
label_list = list(string.digits + string.ascii_uppercase)


def decode(pred_array):
    # argmax返回array中最大值的位置，也就是概率最大的那个位置
    predictions = np.argmax(pred_array, axis=1)

    # 将预测的字母拼接起来
    predicted_word = str.join("", [label_list[pred] for pred in predictions])
    return predicted_word


def predict_captcha(captcha_image):
    """
    :param captcha_image: captcha image path
    :return: str 验证码
    """
    # segment_iamge 抽取小图像，降噪指数默认 2
    image = process(captcha_image)
    subimages = segment_image(image)

    if subimages is not None:
        dataset = np.array(subimages)
        with graph.as_default():
            predicted_word = decode(
                model.predict(dataset.reshape((4, 1, 32, 32))))
        return predicted_word

    # segment_iamge 抽取小图像  降噪指数 3
    image = process(captcha_image, 3)
    subimages = segment_image(image)

    if subimages is not None:
        dataset = np.array(subimages)
        with graph.as_default():
            predicted_word = decode(
                model.predict(dataset.reshape((4, 1, 32, 32))))
        return predicted_word

    # 如果切割图片返回 None 说明没有切割出来 直接不预测
    return None
