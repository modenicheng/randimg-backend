import requests
from icecream import ic
from time import sleep
from . import configs
import threading

def download_pixiv_image_file(image: dict, r=0):
    try:
        url = image['url']
        image_name = image['image_path']
        illust_id = image['id']
        print(f'| {threading.current_thread().name} | Downloading image {image_name}')
    except KeyError:
        print("Image dict not valid")
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
            
        print(f'| {threading.current_thread().name} | Downloaded image {image_name}')
        return image
    except FileNotFoundError as e:
        ic(e)
        exit(-1)
    except Exception as e:
        ic(e)
        sleep(5)
        return download_pixiv_image_file(image, r=r + 1)
    
