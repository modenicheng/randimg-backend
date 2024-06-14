from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

from time import time

def get_dominant_colors(image_path, num_colors=10, scale=1):
    # 打开图像并转换为RGB模式
    image = Image.open(image_path).convert('RGB')

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


def extract_theme_colors(image_path, num_colors=10, scale=1):
    colors = get_dominant_colors(image_path, num_colors, scale=scale)

    # 根据亮度排序颜色
    sorted_colors = sorted(colors, key=get_brightness)

    # 提取暗色主题色（亮度最低的颜色）
    dark_theme_color = sorted_colors[0]
    # 提取亮色主题色（亮度最高的颜色）
    light_theme_color = sorted_colors[-1]
    # 提取主题色（中间亮度的颜色）
    main_theme_color = sorted_colors[len(sorted_colors) // 2]

    return sorted_colors, main_theme_color, light_theme_color, dark_theme_color


def plot_colors(colors):
    # 创建一个显示颜色的条形图
    plt.figure(figsize=(12, 2))
    plt.axis('off')
    plt.imshow([colors], aspect='auto')
    plt.show()


# 示例使用
# image_path = './images/image.jpg'  # 替换为你的图像路径

# colors, main_color, light_color, dark_color = extract_theme_colors(
#     image_path, num_colors=10, scale=0.5)

# print(f"提取的颜色: {colors}")
# print(f"主色调: {main_color}")
