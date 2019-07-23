import numpy as np
from PIL import Image
from skimage import filters
from skimage.morphology import disk, erosion, dilation


def count_white_num(img: np.ndarray, x, y):
    nearDots = 0
    if img[x - 1, y - 1] > 245:
        nearDots += 1
    if img[x - 1, y] > 245:
        nearDots += 1
    if img[x - 1, y + 1] > 245:
        nearDots += 1
    if img[x, y - 1] > 245:
        nearDots += 1
    if img[x, y + 1] > 245:
        nearDots += 1
    if img[x + 1, y - 1] > 245:
        nearDots += 1
    if img[x + 1, y] > 245:
        nearDots += 1
    if img[x + 1, y + 1] > 245:
        nearDots += 1

    return nearDots


def clearNoise(img: np.ndarray, N: int, Z: int):
    """
    8邻域，计算身边八个中白色的个数，大于某个值则该点记为白色。
    :param img: np.ndarray
    :param N: Integer 降噪率 0 <N <8
    :param Z: Integer 降噪次数
    """
    w, h = img.shape
    for i in range(Z):
        for x in range(1, w - 1):
            for y in range(1, h - 1):
                if img[x, y] == 255:
                    continue
                num_ = count_white_num(img, x, y)
                if num_ > N:
                    img[x, y] = 255


def cal_gray_num(color):
    # L = r * .299 + g * .587 + b * .114
    L = 0.212671 * color[0] + 0.715160 * color[1] + 0.072169 * color[2]
    return L


def get_pixel(img, x, y, thresh, N):
    r, g, b = img.getpixel((x, y))
    L = cal_gray_num((r, g, b))
    if L < thresh and (0 <= r <= 60 and 0 <= g <= 90 and 0 <= b <= 90):
        L = True
    else:
        return None

    nearDots = 0
    if L == (cal_gray_num(img.getpixel((x - 1, y - 1))) < thresh):
        nearDots += 1
    if L == (cal_gray_num(img.getpixel((x - 1, y))) < thresh):
        nearDots += 1
    if L == (cal_gray_num(img.getpixel((x - 1, y + 1))) < thresh):
        nearDots += 1
    if L == (cal_gray_num(img.getpixel((x, y - 1))) < thresh):
        nearDots += 1
    if L == (cal_gray_num(img.getpixel((x, y + 1))) < thresh):
        nearDots += 1
    if L == (cal_gray_num(img.getpixel((x + 1, y - 1))) < thresh):
        nearDots += 1
    if L == (cal_gray_num(img.getpixel((x + 1, y))) < thresh):
        nearDots += 1
    if L == (cal_gray_num(img.getpixel((x + 1, y + 1))) < thresh):
        nearDots += 1

    if nearDots < N:
        return (255, 255, 255)
    else:
        return None


def clear_background_noise_line(image, thresh, N, Z):
    """
    根据干扰线都是近黑色，去除干扰线
    :param img: 根据一个点A的值，与周围的8个点的值比较，设定一个值N（0 <N <8），当A的值与周围8个点的相等数小于N时，此点为噪点
    :param thresh: 去噪背景色的阈值
    :param N: Integer 降噪率 0 <N <8
    :param Z: Integer 降噪次数
    """
    w, h = image.size
    for i in range(Z):
        for x in range(1, w - 1):
            for y in range(1, h - 1):
                color = get_pixel(image, x, y, thresh, N)
                if color is not None:
                    image.putpixel((x, y), color)


def convert_grey(image: Image.Image, N: int) -> np.ndarray:
    """
    :param img:  图片
    :return: PIL.Image
    """

    w, h = image.size
    for x in range(w):
        for y in range(h):
            r, g, b = image.getpixel((x, y))

            # 把边缘都清空了
            if x < 15 or y < 5 or w - x < 5 or h - y < 5:
                image.putpixel((x, y), (255, 255, 255))

    # L = R 的值 x 299/1000 + G 的值 x 587/1000+ B 的值 x 114/1000
    clear_background_noise_line(image, 35, N, 2)

    image = image.convert('L')

    image_array = np.array(image)
    return image_array


def denoise(image_array: np.ndarray):
    # 八邻域降噪
    clearNoise(image_array, 5, 2)

    image_array_flatten = image_array.flatten()
    image_array_flatten = image_array_flatten[image_array_flatten < 255]
    image_array_flatten = image_array_flatten[image_array_flatten > 240]

    if image_array_flatten.shape[0] > 300:
        clearNoise(image_array, 4, 1)

    image_array_flatten = image_array.flatten()
    image_array_flatten = image_array_flatten[image_array_flatten < 255]
    image_array_flatten = image_array_flatten[image_array_flatten > 240]
    if image_array_flatten.shape[0] > 280:
        clearNoise(image_array, 5, 1)

    return image_array


def pre_binarization(image: Image.Image,
                     clear_background_noise_line_value: int) -> np.ndarray:
    """
    :param img:  图片
    :return: PIL.Image
    """
    # 转为 灰度图
    image_array = convert_grey(image, clear_background_noise_line_value)
    denoise(image_array)

    return image_array


def morphology_(image_array):
    image_array[image_array < 35] = 0
    image_array[image_array > 245] = 255

    # 中值滤波 -> 开运算
    image_array = filters.median(image_array, disk(1))

    # 腐蚀 黑色区域变大
    image_array = erosion(image_array, disk(1))

    # 膨胀 白色区域
    image_array = dilation(image_array, disk(1))

    image_array[image_array < 35] = 0
    image_array[image_array > 245] = 255

    clearNoise(image_array, 5, 1)

    # 中值滤波 去噪
    for idx in range(2):
        image_array = filters.median(image_array, disk(1))

    return image_array


def process(image: Image.Image,
            clear_background_noise_line_value: int = 2) -> np.ndarray:
    """
    :param image: 传入的是PIL.Image对象
    :return: 返回一个 np.array 类型的图片
    """
    # 二值化
    image_array = pre_binarization(image, clear_background_noise_line_value)

    thresh = filters.threshold_local(image_array, 15)  # 返回一个阈值
    dst = (image_array <= thresh) * 1  # 根据阈值进行分割

    return dst
