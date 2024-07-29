from dogecloud import oss
from icecream import ic

from db import models, database
from sqlalchemy.orm import Session
from db.crud import get_db


def func(key: str, db: Session):
    name = key.split('/')[-1]
    item = db.query(models.Image).filter(models.Image.image_path == name).first()
    if item is None: return
    item.uploaded = True
    db.commit()


storage = oss.OSS()

l = storage.get_file_list()
with get_db() as db:

    for i in l:
        ic(i['key'])
        try:
            func(i['key'], db)
        except Exception as e:
            ic('error', i, e)
