from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, Table, Float, DateTime, Enum
from sqlalchemy.orm import relationship, Mapped
from pydantic import BaseModel
from typing import List
import enum
from .database import Base

image_tag_association = Table(
    'image_tag_association', Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id')),
    Column('tag_id', Integer, ForeignKey('tags.id')))


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    image_path = Column(String)
    source_url = Column(String, nullable=True)
    source_id = Column(Integer, nullable=True)
    source_image_url = Column(String, nullable=True)
    tags = relationship("Tag",
                        secondary=image_tag_association,
                        back_populates="images",
                        lazy=False)
    author_id: Mapped[int] = Column(Integer, ForeignKey("authors.id"))
    author: Mapped['Author'] = relationship(back_populates='images')
    width = Column(Integer)
    height = Column(Integer)
    aspect_ratio = Column(Float(4))  # w / h
    colors = Column(JSON)  # {"color_primary": int, "color_series": list[str]}

    accessable = Column(Boolean, nullable=True, default=None)
    avatar_available = Column(Boolean, nullable=True, default=None)
    uploaded = Column(Boolean, default=False)
    downloaded = Column(Boolean, default=False)
    processed = Column(Boolean, default=False)
    processing = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Image(id={self.id}, image_path={self.image_path}, source_url={self.source_url})>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    translated_name = Column(String)
    images = relationship("Image",
                          secondary=image_tag_association,
                          back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}>"


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    platform = Column(String, nullable=True)
    platform_id = Column(String, nullable=True)
    homepage = Column(String, nullable=True)
    images: Mapped[List['Image']] = relationship(back_populates='author')

    def __repr__(self):
        return f"<Author(id={self.id}, name={self.name}, homepage={self.homepage})>"


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_superuser = Column(Boolean, default=False)


class CrawlerStatus(enum.Enum):
    WAITING = 0
    WORKING = 1
    FINISHED = 2
    FAILED = 3


class CrawlerType(enum.Enum):
    RANKING = 0
    USER = 1
    SEARCH = 2


class Crawler(Base):
    __tablename__ = "crawlers"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    crawl_type = Column(Enum(CrawlerType))
    status = Column(Enum(CrawlerStatus))
    total_pages = Column(Integer)
    processed_pages = Column(Integer)
    target_user_id = Column(String)
    target_start_date = Column(DateTime)
    target_end_date = Column(DateTime)
    target_search_prompt = Column(String) # 搜索爬虫的tag列表，以 `,` 分割
