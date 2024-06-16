from pydantic import BaseModel
from typing import List, Optional, Dict


class TagSchema(BaseModel):
    id: Optional[int]
    name: str
    iamges: Optional[List['ImageSchema']] = []
    num: Optional[int]

    class Config:
        from_attributes = True


class ImageSchema(BaseModel):
    id: Optional[int]
    image_path: str
    source_url: str
    source_id: int
    tags: Optional[List[TagSchema]] = []
    author: Optional['AuthorSchema']
    colors: Optional[Dict]
    width: Optional[int]
    height: Optional[int]
    aspect_ratio: Optional[float]

    class Config:
        from_attributes = True


class AuthorSchema(BaseModel):
    id: Optional[int]
    name: str
    platform: str
    homepage: str
    image: Optional[List['ImageSchema']] = []
    
    class Config:
        from_attributes = True
