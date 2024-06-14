from pydantic import BaseModel
from typing import List, Optional, Dict


class TagSchema(BaseModel):
    id: Optional[int]
    name: str
    articles: Optional[List['ImageSchema']] = []

    class Config:
        orm_mode = True


class ImageSchema(BaseModel):
    id: Optional[int]
    image_path: str
    source_url: str
    tags: Optional[List[TagSchema]] = []
    author: Optional['AuthorSchema']
    colours: Optional[Dict]

    class Config:
        orm_mode = True


class AuthorSchema(BaseModel):
    id: Optional[int]
    name: str
    platform: str
    homepage: str
    image: Optional[List['ImageSchema']] = []
