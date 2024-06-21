from sqlalchemy.orm import Session, joinedload
from . import models, schemas, database
# import models, schemas, database
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from icecream import ic
from configs import CDN_BASE_URL

import random
from faker import Faker
import json

from contextlib import contextmanager

fake = Faker()
session = database.SessionLocal()


@contextmanager
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_admin(db: Session, data: schemas.AdminSchema):
    db.add(models.Admin(**data.model_dump()))
    db.commit()


def create_image(data: dict):
    try:
        db = database.SessionLocal()
        # Create tags if tags are not exist
        tag_objs = []
        for tag in data['tags']:
            tag_obj = db.query(
                models.Tag).filter(models.Tag.name == tag).first()
            if not tag_obj:
                new_tag = models.Tag(name=tag, num=1)
                db.add(new_tag)
                db.commit()
                db.refresh(new_tag)
                tag_objs.append(new_tag)
            else:
                tag_obj.num += 1
                db.commit()
                db.refresh(tag_obj)
                tag_objs.append(tag_obj)

        # Create author if author is not exist
        author_obj = db.query(models.Author).filter(
            models.Author.name == data['author']['name']).first()
        if not author_obj:
            author_data = data['author']
            new_author = models.Author(name=author_data['name'],
                                       platform=author_data['platform'],
                                       homepage=author_data['homepage'])
            db.add(new_author)
            db.commit()
            db.refresh(new_author)
            author = new_author
        else:
            author = author_obj
        db.commit()
        print(data['color'], type(data['color']))
        image = models.Image(title=data['title'],
                             image_path=data['image_path'],
                             source_id=data['source_id'],
                             source_url=data['source_url'],
                             width=data['width'],
                             height=data['height'],
                             aspect_ratio=data['aspect_ratio'],
                             colors=json.dumps(data['color']))
        image.author.append(author)
        image.tags.extend(tag_objs)
        db.add(image)
        db.commit()
        db.refresh(image)
    finally:
        db.close()


def get_illust_ids():
    try:
        db = database.SessionLocal()
        q = db.query(models.Image).all().copy()
        return [i.source_id for i in q]
    except Exception as e:
        print(e)
    finally:
        db.close()


def get_image_by_id(image_id: int):
    I = models.Image
    with get_db() as db:
        img = db.query(models.Image).\
            join(models.image_author_association).\
            join(models.Author, models.Author.id == models.image_author_association.c.author_id).\
            join(models.image_tag_association).\
            join(models.Tag, models.Tag.id == models.image_tag_association.c.tag_id).\
            filter(models.Image.id == image_id).\
            first()
        if img == None:
            return None
        data: schemas.ImageSchema = img
        return data


def get_image_list(offset: int = 0, limit: int = 30):
    with get_db() as db:
        images = db.query(models.Image).offset(offset).limit(limit).all()
        return images


def update_image(data: schemas.ImageManagementSchema):
    with get_db() as db:
        image = db.query(models.Image).filter(models.Image.id == data['id'])
        try:
            data['colors'] = json.dumps(data['colors'])
        except:
            pass
        try:
            del data['author']
        except:
            pass
        try:
            del data['tags']
        except:
            pass
        if image:
            image.update(data)
            db.commit()
            updated_image = db.query(
                models.Image).filter(models.Image.id == data['id']).first()
            return updated_image
        else:
            return None
