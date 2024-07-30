from db import models
from db.crud import get_db
from worker.utils import is_blank_background
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import freeze_support, Process
from sqlalchemy.orm import Session
import queue
import tqdm
import configs


def func(image_path, db: Session):
    db.query(
        models.Image).filter(models.Image.image_path == image_path).update({
            'accessable':
            is_blank_background(configs.IMAGE_DIR + image_path)
        })
    db.commit()
    # print('done', image_path)


if __name__ == '__main__':
    freeze_support()
    e = []

    with get_db() as db:
        l = db.query(
            models.Image).filter(models.Image.accessable == None,
                                 models.Image.downloaded == True).all()
        path_list = [i.image_path for i in l]
        print(l.__len__())
        for path in tqdm.tqdm(path_list):
            func(path, db)
