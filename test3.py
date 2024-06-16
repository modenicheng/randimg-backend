# from dogecloud import oss
# from PIL import Image

# storage = oss.OSS()

# img = Image.open('./images/image2.jpg')
# storage.upload_image_blob(img, 'image2.jpg')

# from db import crud

# res = crud.get_illust_ids()

# print(res)

from dogecloud import oss
from icecream import ic

from db import models, database
from sqlalchemy.orm import Session
import multiprocessing
import queue
from spider import Downloader
import threading

import re

from time import sleep
storage = oss.OSS()

session = database.SessionLocal()
task_queue = queue.Queue()
result_queue = queue.Queue()

upload_queue = queue.Queue()

IMAGE_DOWNLOAD_THREADS = 10

def crawl(id_list):
    global task_queue
    for i in id_list:
        task_queue.put(i)
    
    processes: list[multiprocessing.Process] = []
    for _ in range(IMAGE_DOWNLOAD_THREADS):
        p = threading.Thread(target=worker, args=(task_queue, ))
        processes.append(p)
        p.start()
    
    upload_thread = threading.Thread(target=upload_image_queue)
    upload_thread.start()
    
    task_queue.join()
    upload_queue.join()
    
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
        
def upload_image(image_blob, image_uri: str, retry=0):
    print(f'Uploading {image_uri}')
    
    if retry > 10:
        return -1
    
    storage = oss.OSS()
    
    while retry <= 10:
        try:
            storage.upload_image_blob(image_blob, image_uri)
            return 0
        except Exception as e:
            retry += 1
            print(f'>< Upload {image_uri} retry: {retry} {e}')
            sleep(5)
    
    return -1

def worker(task_queue: queue.Queue):
    print('worker started')
    while True:
        try:
            image = task_queue.get(timeout=3)  # 设置超时以防止永久阻塞
            ic(image)
        except queue.Empty:
            print('worker exiting')
            break
        illust_id = image
        print(f'downloading page {image}')
        image_list = Downloader.pixiv_artwork_page_image_list(illust_id)
        print(f'=> Downloaded page {image}')
        
        threads: list[threading.Thread] = []
        
        for image in image_list:
            image_url = image['image_url']
            print(f'|| Downloading image {image_url}')
            image_blob = Downloader.pixiv_image_blob(image_url)
            try:
                image_path = re.search(r'/([0-9]*_p[0-9]\..*)', image['image_url']).group(1)
                # t = threading.Thread(target=upload_image_wrapper, args=(image_blob, image_path))
                # t.start()
                # threads.append(t)
                upload_queue.put((image_blob, image_path))
            except Exception as e:
                print(f"Error creating thread: {e}")
        
        for t in threads:
            t.join()  # 等待所有线程完成
        
    print('worker finished')

def upload_image_wrapper(image_blob, image_path):
    db = database.SessionLocal()
    try:
        image_obj = db.query(models.Image).filter(models.Image.image_path == image_path).first()
        # if image_obj.uploaded == True:
        #     raise Exception('Already exist')
        if upload_image(image_blob, image_path) == 0:
            image_obj = db.query(models.Image).filter(models.Image.image_path == image_path).first()
            image_obj.uploaded = True
            db.commit()
            db.refresh(image_obj)
            ic(image_obj.uploaded)
    except Exception as e:
        print(e)
    finally:
        db.close()

def upload_image_queue():
    while True:
        image = upload_queue.get()
        print(f'UPLOAD THREAD: Uploading {image[1]}')
        threading.Thread(target=upload_image_wrapper, args=(image[0], image[1])).start()
        upload_queue.task_done()

from contextlib import contextmanager

@contextmanager
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == '__main__':
    with get_db() as db:
        images = db.query(models.Image).filter(models.Image.uploaded == False).all()
        id_list = [i.source_id for i in images]
        
        ic(id_list)
        
        crawl(id_list)

# uploaded_files = storage.get_file_list(limit=400)
# files = [i['key'].replace('s-sh-5182-randimg-1258813047/', '') for i in uploaded_files]
# ic(files)
# db = database.SessionLocal()
# for i in files:
#     img = db.query(models.Image).filter(models.Image.image_path == i).first()
#     if img != None:
#         img.uploaded = True
#         db.commit()
    
# db.close()
