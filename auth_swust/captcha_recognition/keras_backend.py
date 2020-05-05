import string
import numpy as np

from pathlib import Path
from tensorflow.keras import models

# 使用绝对路径 设置model的位置
weight_path = str(Path(__file__).parent.joinpath("model", "tensorflow2", "weights.h5"))
model_path = str(Path(__file__).parent.joinpath("model", "tensorflow2", "cnn.json"))
# 加载模型
with open(model_path) as f:
    model = models.model_from_json(f.read())
    model.load_weights(weight_path)

label_list = list(string.ascii_uppercase + string.digits)


def decode(pred_array):
    # argmax返回array中最大值的位置，也就是概率最大的那个位置
    predictions = np.argmax(pred_array, axis=1)

    # 将预测的字母拼接起来
    predicted_word = str.join("", [label_list[pred] for pred in predictions])
    return predicted_word


def _predict(subimages):
    dataset = np.array(subimages)
    predicted_word = decode(model.predict(dataset.reshape((4, 32, 32, 1))))
    return predicted_word
