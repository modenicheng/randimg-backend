from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, Table, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from .database import Base

image_tag_association = Table(
    'image_tag_association', Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id')),
    Column('tag_id', Integer, ForeignKey('tags.id')))

image_author_association = Table(
    'image_author_association', Base.metadata,
    Column('image_id', Integer, ForeignKey('images.id')),
    Column('author_id', Integer, ForeignKey('authors.id')))

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    image_path = Column(String)
    source_url = Column(String, nullable=True)
    source_id = Column(Integer, nullable=True)
    tags = relationship("Tag",
                        secondary=image_tag_association,
                        back_populates="images",
                        lazy=False)
    author = relationship("Author",
                          secondary=image_author_association,
                          back_populates="images",
                          lazy=False)
    width = Column(Integer)
    height = Column(Integer)
    aspect_ratio = Column(Float(4)) # w / h
    colors = Column(JSON) # {"color_primary": int, "color_series": list[str]}
    
    accessable = Column(Boolean, default=False)
    uploaded = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Image(id={self.id}, image_path={self.image_path}, source_url={self.source_url})>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    num = Column(Integer) # How many images have this tag
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
    homepage = Column(String, nullable=True)
    images = relationship("Image",
                          secondary=image_author_association,
                          back_populates="author")
    
    def __repr__(self):
        return f"<Author(id={self.id}, name={self.name}, homepage={self.homepage})>"

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_superuser = Column(Boolean, default=False)