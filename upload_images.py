from concurrent.futures import ThreadPoolExecutor, as_completed
import crawlers.downloader
import crawlers.uploader
from db import crud
import crawlers
from dogecloud import oss
import configs


def func(d: dict, storage: oss.OSS):
    crawlers.uploader.upload_image(configs.IMAGE_DIR + '/' + d['image_path'],
                      d['image_path'], storage)


storage = oss.OSS()
with ThreadPoolExecutor(max_workers=20) as executor:

    tasks = [
        executor.submit(func, d, storage)
        for d in crud.get_not_uploaded_illusts()
    ]
    for t in as_completed(tasks):
        print(t.result())
