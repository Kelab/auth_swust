import numpy as np
from PIL import Image
from skimage import filters
from skimage.morphology import disk
from loguru import logger


cord_list = [[0, 1], [1, 0], [1, 1], [-1, -1], [-1, 0], [-1, 1], [0, -1], [1, -1]]


def enhance(image: np.ndarray) -> np.ndarray:
    """分离有效信息和干扰信息 把背景的灰点去除"""
    result = image.copy()
    w, h = image.shape
    thres = filters.threshold_otsu(image)
    logger.debug("ostu thres: {}", thres)
    window = []
    for i in range(w):
        for j in range(h):
            window = [(i, j)]
            for cord in cord_list:
                i = i + cord[0]
                j = j + cord[1]
                if 0 <= i < w and 0 <= j < h:
                    window.append((i, j))

            window.sort(key=lambda e: image[e])
            (x, y) = window[len(window) // 2]
            diff = abs(int(image[x, y]) - int(image[i, j]))

            if image[i, j] > 230 and diff < (255 - thres):  # 若差值小于阈值则进行“强化”
                result[i, j] = 255
            elif image[i, j] < 20 and diff > thres:
                result[i, j] = 255

    return result


def pre_binarization(image: Image.Image) -> np.ndarray:
    """二值化之前：灰度、去噪
    """
    w, h = image.size
    # 因为验证码位置相对固定，所以将几个边界都置为白色
    for x in range(w):
        for y in range(h):
            if x < 17 or y < 9 or h - y < 3:
                image.putpixel((x, y), (255, 255, 255))
    # 转为 灰度图
    image = image.convert("L")
    image_array: np.ndarray = np.array(image)
    for i in range(2):
        image_array = enhance(image_array)
        image_array = filters.median(image_array, disk(1))

    return image_array


def process(image: Image.Image) -> np.ndarray:
    """
    :param image: 传入的是PIL.Image对象
    :return: 返回一个 np.array 的二值化后的图片
    """
    image_array = pre_binarization(image)
    thresh = filters.threshold_local(image_array, 15)  # 返回一个阈值
    dst = (image_array <= thresh) * 1  # 根据阈值进行分割

    return dst
