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
    title: str
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

class ImageManagementSchema(BaseModel):
    id: Optional[int] = None
    image_path: str
    source_url: Optional[str] = None
    source_id: Optional[int] = None
    tags: Optional[List[TagSchema]] = []
    author: Optional[List['AuthorSchema']] = []
    colors: Optional[Dict] = None
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None
    accessable: Optional[bool] = False
    uploaded: Optional[bool] = False
    title: Optional[str] = None

    class Config:
        from_attributes = True

class AdminSchema(BaseModel):
    # id: Optional[int]
    username: str
    is_superuser: Optional[bool] = True
    password: str
    
    class Config:
        from_attributes = True