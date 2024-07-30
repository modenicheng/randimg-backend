from db import models
from db.crud import get_db
from worker.utils import is_blank_background
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import freeze_support, Process, Pool
from sqlalchemy.orm import Session
import queue
import tqdm
import configs
from functools import partial
import cv2


def func(image_path):
    with get_db() as db:
        try:
            db.query(models.Image).filter(
                models.Image.image_path == image_path).update({
                    'accessable':
                    not is_blank_background(configs.IMAGE_DIR + image_path)
                })
            db.commit()
        except cv2.error:
            db.query(models.Image).filter(
                models.Image.image_path == image_path).update(
                    {'accessable': False})
            db.commit()


if __name__ == '__main__':
    freeze_support()

    with get_db() as db:
        l = db.query(
            models.Image).filter(models.Image.accessable == None,
                                 models.Image.downloaded == True).all()
        path_list = [i.image_path for i in l]
        del l
        with Pool(4) as p:
            list(
                tqdm.tqdm(p.imap(func, path_list),
                          total=len(path_list),
                          desc='Processing images'))
        print('Done.')
