from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, Table, Float
from sqlalchemy.orm import relationship

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
    image_path = Column(String)
    source_url = Column(String, nullable=True)
    tags = relationship("Tag",
                        secondary=image_tag_association,
                        back_populates="images")
    author = relationship("Author",
                          secondary=image_author_association,
                          back_populates="images")
    resolution_ratio = Column(String) # "width:height"
    aspect_ratio = Column(Float(4)) # 
    colours = Column(JSON) # {"colour_primary": int, "colour_series": list[str]}

    def __repr__(self):
        return f"<Image(id={self.id}, image_path={self.image_path}, source_url={self.source_url})>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    images = relationship("Image",
                          secondary=image_tag_association,
                          back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}>"


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    platform = Column(String)
    homepage = Column(String, index=True)
    images = relationship("Image",
                          secondary=image_author_association,
                          back_populates="author")
