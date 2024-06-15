from sqlalchemy.orm import Session
from . import models, schemas, database
# import models, schemas, database
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from icecream import ic

import random
from faker import Faker
import json

fake = Faker()
session = database.SessionLocal()


# def generate_random_data():
#     entry = {
#         'title':
#         fake.sentence(),
#         'illust_id':
#         random.randint(100000, 999999),
#         'user_id':
#         random.randint(1000, 9999),
#         'user_name':
#         fake.name(),
#         'tags':
#         random.sample(['nature', 'technology', 'art', 'abstract', 'portrait'],
#                       random.randint(1, 5)),
#     }

#     image = {
#         'width': random.randint(300, 1920),
#         'height': random.randint(300, 1080),
#         'aspect_ratio': round(random.uniform(0.5, 2.0), 2)
#     }

#     main_color = [random.randint(0, 255) for _ in range(3)]
#     sorted_colors = [[random.randint(0, 255) for _ in range(3)]
#                      for _ in range(random.randint(1, 5))]

#     db_data = {
#         'title': entry['title'],
#         'image_path': f"/path/to/image_{entry['illust_id']}.jpg",
#         'source_id': entry['illust_id'],
#         'source_url': f"https://www.pixiv.net/artworks/{entry['illust_id']}",
#         'width': image['width'],
#         'height': image['height'],
#         'aspect_ratio': image['aspect_ratio'],
#         'tags': entry['tags'],
#         'author': {
#             'platform': 'pixiv',
#             'platform_id': entry['user_id'],
#             'homepage': f'https://www.pixiv.net/users/{entry["user_id"]}',
#             'name': entry['user_name']
#         },
#         'color': {
#             'color_primary': main_color,
#             'color_series': [list(i) for i in sorted_colors]
#         }
#     }

#     return db_data


def create_image(data: dict):
    try:
        db = database.SessionLocal()
        # Create tags if tags are not exist
        tag_objs = []
        for tag in data['tags']:
            tag_obj = db.query(models.Tag).filter(models.Tag.name == tag).first()
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