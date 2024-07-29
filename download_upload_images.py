from concurrent.futures import ThreadPoolExecutor, as_completed
import crawlers.downloader
import crawlers.uploader
from db import crud
import requests
import crawlers
from dogecloud import oss
import configs

def func(d: dict):
    # crawlers.downloader.download_pixiv_image_file(d)
    crawlers.uploader(configs.IMAGE_DIR + '/' + d['image_path'])


storage = oss.OSS()
with ThreadPoolExecutor(max_workers=10) as executor:

    tasks = [
        executor.submit(func, d, storage)
        for d in crud.get_not_downloaded_illusts()
    ]
    r = [t.result() for t in as_completed(tasks)]
