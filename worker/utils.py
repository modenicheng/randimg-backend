from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from . import configs
import os
import cv2

from icecream import ic

def get_downloaded_image_list():
    return [
        os.path.join(configs.IMAGE_DIR, i).split('/')[-1]
        for i in os.listdir(configs.IMAGE_DIR)
    ][1:]


def get_dominant_colors(image: Image.Image | str, num_colors=10, scale=0.5):
    # 打开图像并转换为RGB模式
    if type(image) == str:
        image = Image.open(image).convert('RGB')

    image = image.resize((int(image.width * scale), int(image.height * scale)))
    # 将图像转换为numpy数组
    image_np = np.array(image)
    # 重塑图像数组为二维数组
    pixels = image_np.reshape(-1, 3)

    # 使用KMeans聚类算法提取主色调
    kmeans = KMeans(n_clusters=num_colors, random_state=42)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)

    return colors


def get_brightness(color):
    # 计算颜色的亮度，公式为：0.299*R + 0.587*G + 0.114*B
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]


def extract_theme_colors(image: Image.Image | str, num_colors=10, scale=0.7):
    colors = get_dominant_colors(image, scale=scale)

    # 根据亮度排序颜色
    sorted_colors = sorted(colors.tolist(), key=get_brightness)

    # 提取主题色（中间亮度的颜色）
    main_theme_color = sorted_colors[len(sorted_colors) // 2]

    return list([list(i) for i in sorted_colors]), list(main_theme_color)


def plot_colors(colors):
    # 创建一个显示颜色的条形图
    plt.figure(figsize=(12, 2))
    plt.axis('off')
    plt.imshow([colors], aspect='auto')
    plt.show()


# 示例使用
# image_path = './images/image.jpg'  # 替换为你的图像路径

# colors, main_color = extract_theme_colors(
#     image_path, num_colors=10, scale=0.5)

# main_color = list(main_color)

# print(f"提取的颜色: {colors}")
# print(f"主色调: {main_color}, {type(main_color)}")

# Image HASH

import imagehash


def phash(img_path: str):
    highfreq_factor = 1
    hash_size = 12

    result = imagehash.phash(Image.open(img_path),
                             hash_size=hash_size,
                             highfreq_factor=highfreq_factor)
    return result


def hash_similarity(hash1: imagehash.ImageHash, hash2: imagehash.ImageHash):
    return 1 - (hash1 - hash2) / len(hash1.hash)**2


def get_dominant_colors_v2(file_path: str, scale: float = 0.5, num_colors: int = 10):
    image: Image = Image.open(file_path).convert('RGB')
    image = image.resize(
        (int(image.width * scale), int(image.height * scale)))
    result = image.convert('P', palette=Image.Palette.ADAPTIVE, colors=num_colors)
    result = result.convert('RGB')
    ic(result)

def is_blank_background(file, scale_factor: float = 0.5):
    if type(file) == str:
        try:
            image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
        except FileNotFoundError:
            print('File not exist.')
            return
    else:
        image = cv2.imdecode(file, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (0, 0), fx=scale_factor, fy=scale_factor)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    total_pix = image.shape[0] * image.shape[1]
    white_area_ratio = np.sum(image >= 210) / total_pix
    black_area_ratio = np.sum(image <= 15) / total_pix
    del image
    if white_area_ratio >= 0.53 or black_area_ratio >= 0.4:
        return True
    else:
        return False