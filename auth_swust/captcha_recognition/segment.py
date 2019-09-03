import numpy as np
from PIL import Image
from skimage.measure import label, regionprops
from skimage.morphology import remove_small_objects


def segment_image(image_array: np.ndarray, origin_image: Image.Image = None):
    # 连通分支切割
    subimages = segment_image_by_region(image_array)
    if len(subimages) == 4:
        return [add_padding(image) for image in subimages]

    # 没有找到四张小图像的情况，直接返回 None
    return None


def segment_image_by_region(image_array: np.ndarray) -> np.ndarray:
    """
    通过连通分支来切割，对各个字符比较分离的验证码比较好切割
    """
    # 将整张图片转置，以便于从上向下按顺序进行搜索连通分支。
    image = image_array.transpose()
    # 我们要做的第一件事就是检测每个字母的位置，这就要用到`scikit-image`的`label`函数，它能找出图像中像素值相同且又连接在一起的像素块。这有点像连通分支。`label`函数的参数为图像数组，返回跟输入同型的数组。在返回的数组中，图像**连接在一起的区域**用不同的值来表示，在这些区域以外的像素用0来表示。
    labeled_image: np.ndarray = label(image, connectivity=2)
    labeled_image = remove_small_objects(labeled_image,
                                         min_size=30,
                                         connectivity=2)

    # 抽取每一张小图像，将它们保存到这个列表中。
    subimages = []

    # `scikit-image`库还提供抽取连续区域的函数：`regionprops`。遍历这些区域，分别对它们进行处理。
    for region in regionprops(labeled_image):
        start_x, start_y, end_x, end_y = region.bbox
        # 乘积大于16，排除连通分支较小的块
        if (end_x - start_x) * (end_y - start_y) >= 16:
            img_region = image[start_x:end_x, start_y:end_y]

            img_region[img_region == 0] = 123
            img_region[img_region == 1] = 0
            img_region[img_region == 123] = 1

            # 用这两组坐标作为索引就能抽取到小图像（`image`对象为`numpy`数组，可以直接用索引值），然后，把它保存到`subimages`列表中。
            subimages.append(img_region.transpose())

    # 最后返回找到的小图像，每张小图像包含图片中的一个字母区域。
    return subimages


def add_padding(img: np.ndarray) -> np.ndarray:
    # 创建一个边长为 len_ 的正方形
    len_ = 32
    square = np.ones((len_, len_))

    width_diff = len_ - img.shape[0]
    height_diff = len_ - img.shape[1]

    x_start = width_diff // 2
    y_start = height_diff // 2
    if img.shape[0] + x_start < len_ and img.shape[1] + y_start < len_:
        for x in range(img.shape[0]):
            for y in range(img.shape[1]):
                square[x + x_start, y + y_start] = img[x, y]
        return square
    return square
