from concurrent.futures import ThreadPoolExecutor, as_completed
import crawlers.downloader
from db import crud
import requests
import crawlers
from dogecloud import oss


def func(d: dict, storage: oss.OSS):
    crawlers.downloader.download_pixiv_image_file(d)
    print(d['image_path'], 'uploading')
    storage.upload_image_file(d['image_path'], d['image_path'])
    return d


storage = oss.OSS()
with ThreadPoolExecutor(max_workers=10) as executor:

    tasks = [
        executor.submit(func, d, storage)
        for d in crud.get_not_downloaded_illusts()
    ]
    r = [t.result() for t in as_completed(tasks)]
