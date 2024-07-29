from sqlalchemy.orm import Session, joinedload
from . import models, schemas, database
# import models, schemas, database
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, and_
from icecream import ic
from configs import CDN_BASE_URL

import random
from faker import Faker
import json
import time
from contextlib import contextmanager

from typing import Literal

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

        img = db.query(models.Image).filter(
            models.Image.image_path == image_data.get('image_path')).first()
        if img != None:
            img.title = image_data['title'],
            img.image_path = image_data['image_path'],
            img.source_id = image_data.get('id'),
            img.source_url = image_data.get('source_url'),
            img.width = image_data['width'],
            img.height = image_data['height'],
            img.aspect_ratio = image_data.get('aspect_ratio'),
            img.colors = image_data.get('colors')
            img.source_image_url = image_data.get('image_url')
            db.commit()
            db.refresh(img)
            return image_data
        tag_objs = []
        for tag in image_data['tags']:
            tag_obj = db.query(
                models.Tag).filter(models.Tag.name == tag['name']).first()
            if not tag_obj:
                new_tag = models.Tag(
                    name=tag['name'],
                    translated_name=tag.get('translated_name'))
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
            or_(
                models.Author.name == image_data['author']['name'],
                models.Author.platform_id == str(
                    image_data['author']['platform_id']))).first()
        if not author_obj:
            author_data = image_data['author']
            new_author = models.Author(name=author_data['name'],
                                       platform=author_data['platform'],
                                       platform_id=str(
                                           author_data['platform_id']))
            db.add(new_author)
            db.commit()
            db.refresh(new_author)
            author = new_author
        else:
            author = author_obj

        source_id = image_data['id']
        source_url = f'https://www.pixiv.net/artworks/{source_id}'
        try:
            file_name = image_data['image_url'].split('/')[-1]
        except KeyError:
            file_name = image_data.get('image_path')
        image = models.Image(title=image_data['title'],
                             image_path=file_name,
                             source_id=source_id,
                             source_url=source_url,
                             width=image_data['width'],
                             height=image_data['height'],
                             source_image_url=image_data.get('image_url'),
                             aspect_ratio=image_data.get('aspect_ratio'),
                             colors=image_data.get('colors'))
        author.images.append(image)
        image.tags.extend(tag_objs)
        db.add(image)
        db.commit()
        db.refresh(image)
        return image


def uploaded_image(image_path: str):
    """Call this func after image is uploaded to cloud storage

    Args:
        image_path (str): _description_
    """
    with get_db() as db:
        img = db.query(models.Image).filter(
            models.Image.image_path == image_path).first()
        while img == None:
            time.sleep(1)
            img = db.query(models.Image).filter(
                models.Image.image_path == image_path).first()
        img.uploaded = True
        db.commit()


def downloaded_image(image_path: str):
    """Call this func after image is downloaded to local storage
    Args:
        image_path (str): The key of the image
    """
    with get_db() as db:
        img = db.query(models.Image).filter(
            models.Image.image_path == image_path).first()
        while img == None:
            time.sleep(1)
            img = db.query(models.Image).filter(
                models.Image.image_path == image_path).first()
        img.downloaded = True
        db.commit()


def processed_image(image_path: str):
    with get_db() as db:
        img = db.query(models.Image).filter(
            models.Image.image_path == image_path).first()
        while img == None:
            time.sleep(1)
            img = db.query(models.Image).filter(
                models.Image.image_path == image_path).first()
        img.processed = True
        db.commit()


def get_illust_ids():
    try:
        db = database.SessionLocal()
        q = db.query(models.Image).all().copy()
        return [i.source_id for i in q]
    except Exception as e:
        print(e)
    finally:
        db.close()


def get_exist_images() -> list:
    with get_db() as db:
        images = db.query(
            models.Image).filter(models.Image.uploaded == True).all()
        image_list = [image.image_path for image in images]
        return image_list


def get_uploaded_images() -> list:
    """Get uploaded images from database

    Returns:
        list: image_list = [image.image_path for image in images]
    """
    with get_db() as db:
        images = db.query(
            models.Image).filter(models.Image.uploaded == True).all()
        image_list = [image.image_path for image in images]
        return image_list


def get_unprocessed_images(ids: bool = False) -> list:
    with get_db() as db:
        images = db.query(models.Image).filter(
            models.Image.processed == False,
            models.Image.processing == False).all()
        if ids:
            image_list = [{
                'id': image.id,
                "image_path": image.image_path
            } for image in images]
        else:
            image_list = [image.image_path for image in images]
        return image_list


def get_downloaded_illusts() -> list:
    with get_db() as db:
        images = db.query(
            models.Image).filter(models.Image.downloaded == True).all()
        image_list = [image.source_id for image in images]
        return image_list


def is_illust_downloaded(illust_id: int | str):
    illust_id = int(illust_id)
    with get_db() as db:
        image = db.query(
            models.Image).filter(models.Image.source_id == illust_id).first()
        return False if image == None else True


def is_image_uploaded(key: str):
    with get_db() as db:
        image = db.query(
            models.Image).filter(models.Image.image_path == key).first()
        if image is None:
            return False
        return image.uploaded


def is_illust_detail_downloaded(source_id: int) -> bool:
    with get_db() as db:
        image = db.query(
            models.Image).filter(models.Image.source_id == source_id).first()
        if image is None:
            return False
        return image.downloaded


def is_image_url_collected(image_name: str):
    with get_db() as db:
        image = db.query(models.Image).filter(
            models.Image.image_path == image_name).first()
        if image is None:
            return False
        if image.source_image_url:
            return True
        else:
            return False


def is_image_downloaded(key: str) -> bool:
    with get_db() as db:
        image = db.query(
            models.Image).filter(models.Image.image_path == key).first()
        if image is None:
            return False
        return image.downloaded


def is_image_processed(key: str) -> bool:
    with get_db() as db:
        image = db.query(
            models.Image).filter(models.Image.image_path == key).first()
        if image is None:
            return False
        return image.processed


def get_illust_images(illust_id: int) -> list:
    with get_db() as db:
        images = db.query(
            models.Image).filter(models.Image.source_id == illust_id).all()
        return [{
            'id':
            image.source_id,
            "image_path":
            image.image_path,
            "title":
            image.title,
            'source_id':
            image.source_id,
            "aspect_ratio":
            image.aspect_ratio,
            "source_url":
            image.source_url,
            "width":
            image.width,
            "height":
            image.height,
            "colors":
            image.colors,
            "url":
            image.source_image_url,
            "author": {
                'id': image.author.id,
                'name': image.author.name,
                'platform_id': image.author.platform_id,
                'platform': image.author.platform
            },
            "tags": [{
                "id": tag.id,
                "name": tag.name,
                "translated_name": tag.translated_name
            } for tag in image.tags],
        } for image in images]


def get_image_by_id(image_id: int, is_admin: bool = False):
    with get_db() as db:
        image = db.query(models.Image).\
            join(models.image_tag_association).\
            join(models.Tag, models.Tag.id == models.image_tag_association.c.tag_id).\
            filter(models.Image.id == image_id).\
            options(joinedload(models.Image.author)).\
            first()
        if image == None:
            return None
        if image.accessable == False and not is_admin:
            return None
        data: schemas.ImageSchema = {
            'id':
            image.id,
            "src":
            CDN_BASE_URL + image.image_path,
            "image_path":
            image.image_path,
            "title":
            image.title,
            'source_id':
            image.source_id,
            "aspect_ratio":
            image.aspect_ratio,
            "source_url":
            image.source_url,
            "width":
            image.width,
            "height":
            image.height,
            "colors":
            image.colors,
            "author": {
                'id': image.author.id,
                'name': image.author.name,
                'platform_id': image.author.platform_id,
                'platform': image.author.platform
            },
            "tags": [{
                "id": tag.id,
                "name": tag.name,
                "translated_name": tag.translated_name
            } for tag in image.tags],
        }
        return data


def get_image_list(
    offset: int = 0,
    limit: int = 30,
    desc: bool = True,
    ratio_floor: float = 0,
    ratio_ceil: float = 10,
    tags: str = None,
    author: str | int = None,
    more_data: bool = False,
    full_list: bool = False,
    raw_obj: bool = False,
    only_ids: bool = False,
    accessable: Literal[True, False, 'all'] = 'all'
) -> list[models.Image] | list[dict]:
    """
    :params:
        :author      Either id or name could be recognized. Fuzzy when using name.
        :tags        Use `,` to split.
        :full_list   Equally using `limit=None`
    """

    with get_db() as db:
        if full_list:
            offset = 0
            limit = None

        if tags:
            images = db.\
                query(models.Image).\
                join(models.Image.author).\
                join(models.image_tag_association).\
                join(models.Tag, models.Tag.id == models.image_tag_association.c.tag_id).\
                filter(
                    and_(
                    models.Image.uploaded == True,
                    and_(models.Image.accessable == accessable) if accessable != 'all' else or_(models.Image.accessable == True, models.Image.accessable == False),
                    models.Image.aspect_ratio >= ratio_floor,
                    models.Image.aspect_ratio <= ratio_ceil),
                    or_(models.Author.id == author if type(author) == int else
                        models.Author.name.like("%" + author +
                                                "%")) if author != None else True,
                    or_(models.Tag.name.in_(tags.split(',')),
                        models.Tag.translated_name.in_(tags.split(',')))
                    if tags != None and tags != '' else True,
                ).\
                order_by(models.Image.id.desc() if desc else models.Image.id.asc()).\
                offset(offset).\
                limit(limit).\
                all()
        else:
            images = db.\
                query(models.Image).\
                join(models.Image.author).\
                filter(
                    and_(
                    models.Image.uploaded == True,
                    models.Image.processed ==True,
                    and_(models.Image.accessable == accessable) if accessable != 'all' else or_(models.Image.accessable == True, models.Image.accessable == False),
                    models.Image.aspect_ratio >= ratio_floor,
                    models.Image.aspect_ratio <= ratio_ceil),
                    or_(models.Author.id == author if type(author) == int else
                        models.Author.name.like("%" + author +
                                                "%")) if author != None else True,
                    or_(models.Tag.name.in_(tags.split(',')),
                        models.Tag.translated_name.in_(tags.split(',')))
                    if tags != None and tags != '' else True,
                ).\
                order_by(models.Image.id.desc() if desc else models.Image.id.asc()).\
                offset(offset).\
                limit(limit).\
                all()

        if raw_obj and not only_ids:
            return images
        if only_ids:
            return [i.id for i in images]
        if more_data:
            data = [{
                'id':
                image.id,
                "src":
                CDN_BASE_URL + image.image_path,
                "title":
                image.title,
                'source_id':
                image.source_id,
                "aspect_ratio":
                image.aspect_ratio,
                "primary_color":
                image.colors.get('primary_color')
                if image.colors != None else None,
                "accessable":
                image.accessable,
                "author": {
                    'id': image.author.id,
                    'name': image.author.name,
                    'platform_id': image.author.platform_id,
                    'platform': image.author.platform
                },
                "tags": [{
                    "id": tag.id,
                    "name": tag.name,
                    "translated_name": tag.translated_name
                } for tag in image.tags],
            } for image in images]
        else:
            data = [{
                'id':
                image.id,
                "src":
                CDN_BASE_URL + image.image_path,
                "title":
                image.title,
                "author":
                image.author_id,
                "tags": [{
                    "id": tag.id,
                    "name": tag.name,
                    "translated_name": tag.translated_name
                } for tag in image.tags],
                'source_id':
                image.source_id,
                "aspect_ratio":
                image.aspect_ratio,
                "primary_color":
                image.colors.get('primary_color')
                if image.colors != None else None,
            } for image in images]
        return data


def update_image(data: schemas.ImageManagementSchema, db: Session):
    image = db.query(models.Image).filter(models.Image.id == data['id'])
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


def update_image_colors_by_image_path(image_path: str,
                                      data: dict) -> models.Image | None:
    with get_db() as db:
        image = db.query(models.Image).filter(
            models.Image.image_path == image_path).first()
        if image is not None:
            image.colors = data['colors']
            image.processed = data['processed']
            db.commit()
            db.refresh(image)
            return image
        else:
            return None


def get_unprocessed_image_and_change_status():
    with get_db() as db:
        image = db.query(models.Image).filter(
            models.Image.processed == False, models.Image.processing == False,
            models.Image.downloaded == True).first()

        if image == None:
            return None
        image.processing = True
        db.commit()
        db.refresh(image)
        return image


def get_tags():
    with get_db() as db:
        tags = db.query(models.Tag).all()
        return [{
            "id": tag.id,
            "name": tag.name,
            "translated_name": tag.translated_name,
            "search_string": tag.name + '|' + str(tag.translated_name)
        } for tag in tags]


def create_crawler(data: schemas.CreateCrawlerSchema, db: Session):
    crawler = models.Crawler(**data.model_dump())
    db.add(crawler)
    db.commit()
    db.refresh(crawler)
    return crawler


def get_not_downloaded_illusts():
    with get_db() as db:
        l = db.query(models.Image).filter(models.Image.downloaded == False).all()
        return [{'id': i.id, 'url': i.source_image_url, 'image_path': i.image_path} for i in l]

def get_not_uploaded_illusts():
    with get_db() as db:
        l = db.query(models.Image).filter(models.Image.uploaded == False).all()
        return [{'id': i.id, 'url': i.source_image_url, 'image_path': i.image_path} for i in l]
