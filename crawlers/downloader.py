import requests
import re
from icecream import ic
from time import sleep
from . import configs


def download_pixiv_image_file(url: str, r=0):
    image_name = url[url.rfind("/") + 1:]
    result = re.search(r"/(\d+)_", url)
    illust_id = result.group(1)
    headers = {
        "Referer": f"https://www.pixiv.net/artworks/{illust_id}",
        **configs.HEADERS
    }
    try:
        res = requests.get(url,
                           headers=headers,
                           stream=True,
                           proxies=configs.PROXIES)
        assert res.status_code == 200
        with open(f"{configs.IMAGE_DIR}/{image_name}", "wb") as f:
            f.write(res.content)
    except FileNotFoundError as e:
        ic(e)
        exit(-1)
    except Exception as e:
        ic(e)
        sleep(5)
        return download_pixiv_image_file(url, r=r + 1)
