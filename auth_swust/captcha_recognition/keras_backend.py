import string
import numpy as np
import tensorflow as tf

from pathlib import Path
from keras.models import model_from_yaml

# 使用绝对路径 设置model的位置
weight_path = str(
    Path(__file__).parent.joinpath("model", "keras_cnn", "keras_cnn.weight")
)
model_path = str(Path(__file__).parent.joinpath("model", "keras_cnn", "keras_cnn.yml"))
# 加载模型
with open(model_path) as f:
    model = model_from_yaml(f.read())
    model.load_weights(weight_path)

graph = tf.compat.v1.get_default_graph()

label_list = list(string.ascii_uppercase + string.digits)


def decode(pred_array):
    # argmax返回array中最大值的位置，也就是概率最大的那个位置
    predictions = np.argmax(pred_array, axis=1)

    # 将预测的字母拼接起来
    predicted_word = str.join("", [label_list[pred] for pred in predictions])
    return predicted_word


def _predict(subimages):
    dataset = np.array(subimages)
    global graph
    with graph.as_default():
        predicted_word = decode(model.predict(dataset.reshape((4, 1, 32, 32))))
    return predicted_word
