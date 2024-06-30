import requests
import json
import datetime
import re

from PIL import Image

from . import configs

from icecream import ic
from io import BytesIO

import os

from time import sleep


def pixiv_image_blob(url: str, save_path: str = './tmp_images', r=0):
    image_name = url[url.rfind("/") + 1:]
    result = re.search(r"/(\d+)_", url)
    illust_id = result.group(1)
    headers = {
        "Referer": f"https://www.pixiv.net/artworks/{illust_id}",
        **configs.HEADERS
    }
    try:
        res = requests.get(url, headers=headers, stream=True)
        assert res.status_code == 200
        image = Image.open(BytesIO(res.content)).convert('RGB')
        return image
    except Exception as e:
        ic(e)
        sleep(5)
        return pixiv_image_blob(url, r=r + 1)

def pixiv_artwork_page_image_list(illust_id: int):
    url = f"https://www.pixiv.net/ajax/illust/{illust_id}/pages?lang=zh"
    print(f'Collecting image list of {illust_id}')
    try:
        res = requests.get(url,
                           headers=configs.HEADERS.update({
                               "Referer":
                               f"https://www.pixiv.net/artworks/{illust_id}",
                               "x-user-id":
                               str(configs.USER_ID),
                           }))
    except:
        sleep(5)
        return pixiv_artwork_page_image_list(illust_id)
    if res.status_code != 200:
        print(res.status_code, res.reason)

    data = res.json()
    image_list = data['body']
    map_result = map(
        lambda x: {
            'image_url': x['urls']['original'],
            'width': x['width'],
            'height': x['height'],
            'aspect_ratio': x['width'] / x['height']
        }, image_list)

    return [i for i in map_result]
