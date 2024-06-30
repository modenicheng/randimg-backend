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
                new_tag = models.Tag(
                    name=tag, translated_name=tag.get('translated_name'))
                db.add(new_tag)
                db.commit()
                db.refresh(new_tag)
                tag_objs.append(new_tag)
            else:
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
        return image
    finally:
        db.close()


def create_image_rebuild(image_data: dict):
    with get_db() as db:
        tag_objs = []
        for tag in image_data['tags']:
            tag_obj = db.query(
                models.Tag).filter(models.Tag.name == tag['name']).first()
            if not tag_obj:
                new_tag = models.Tag(
                    name=tag['name'], translated_name=tag.get('translated_name'))
                db.add(new_tag)
                db.commit()
                db.refresh(new_tag)
                tag_objs.append(new_tag)
            else:
                db.commit()
                db.refresh(tag_obj)
                tag_objs.append(tag_obj)

        # Create author if author is not exist
        author_obj = db.query(models.Author).filter(
            models.Author.name == image_data['author']['name'],
            models.Author.platform_id == str(image_data['author']['platform_id'])
            ).first()
        if not author_obj:
            author_data = image_data['author']
            new_author = models.Author(name=author_data['name'],
                                       platform=author_data['platform'],
                                       platform_id=str(author_data['platform_id']))
            db.add(new_author)
            db.commit()
            db.refresh(new_author)
            author = new_author
        else:
            author = author_obj
        
        source_id = image_data['id']
        source_url = f'https://www.pixiv.net/artworks/{source_id}'
        file_name = image_data['image_url'].split('/')[-1]
        image = models.Image(title=image_data['title'],
                             image_path=file_name,
                             source_id=source_id,
                             source_url=source_url,
                             width=image_data['width'],
                             height=image_data['height'],
                             aspect_ratio=image_data['aspect_ratio'],
                             colors=image_data['colors'])
        author.images.append(image)
        image.tags.extend(tag_objs)
        db.add(image)
        db.commit()
        db.refresh(image)
        return image


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
            join(models.image_tag_association).\
            join(models.Tag, models.Tag.id == models.image_tag_association.c.tag_id).\
            filter(models.Image.id == image_id).\
            first()
        if img == None:
            return None
        data: schemas.ImageSchema = img
        return data


def get_image_list(offset: int = 0,
                   limit: int = 30,
                   accessable=True,
                   more_data=False):
    with get_db() as db:
        images = db.query(models.Image).filter(
            models.Image.uploaded == True, models.Image.accessable ==
            accessable).offset(offset).limit(limit).all()
        if more_data:
            data = [{
                'id': image.id,
                "src": CDN_BASE_URL + image.image_path,
                "title": image.title,
                'source_id': image.source_id,
                "aspect_ratio": image.aspect_ratio,
                "primary_color": json.loads(image.colors)['color_primary'],
                "accessable": image.accessable,
                "author": image.author,
                "tags": image.tags,
            } for image in images]
        else:
            data = [{
                'id': image.id,
                "src": CDN_BASE_URL + image.image_path,
                "title": image.title,
                "author": image.author,
                "tags": image.tags,
                'source_id': image.source_id,
                "aspect_ratio": image.aspect_ratio,
                "primary_color": json.loads(image.colors)['color_primary'],
            } for image in images]
        return data


def update_image(data: schemas.ImageManagementSchema, db: Session):
    image = db.query(models.Image).filter(models.Image.id == data['id'])
    try:
        data['colors'] = json.dumps(data['colors'])
    except:
        pass
    # 俩外键字段摆了，不会有人想改这玩意
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
