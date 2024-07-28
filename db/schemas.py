from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict
from . import models


class TagSchema(BaseModel):
    id: Optional[int]
    name: str
    translated_name: Optional[str]
    iamges: Optional[List['ImageSchema']] = []

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
    platform: Optional[str] = None
    homepage: Optional[str] = None
    image: Optional[List['ImageSchema']] = []

    class Config:
        from_attributes = True


class ImageManagementSchema(BaseModel):
    id: Optional[int] = None
    # image_path: Optional[str]
    source_url: Optional[str] = None
    source_id: Optional[int] = None
    tags: Optional[List[TagSchema]] = []
    author: Optional['AuthorSchema'] = None
    colors: Optional[Dict] = None
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None
    accessable: Optional[bool] = False
    uploaded: Optional[bool] = False
    title: Optional[str] = None
    processed: Optional[bool] = False
    processing: Optional[bool] = False

    class Config:
        from_attributes = True


class AdminSchema(BaseModel):
    # id: Optional[int]
    username: str
    is_superuser: Optional[bool] = True
    password: str

    class Config:
        from_attributes = True


class CreateCrawlerSchema(BaseModel):
    id: Optional[int] = None
    task_name: str = ''
    crawl_type: models.CrawlerType = models.CrawlerType.USER
    target_user_id: Optional[str] = None # 用户爬虫的id列表，以 `,` 分割
    target_start_date: Optional[datetime] = None
    target_end_date: Optional[datetime] = None
    target_search_prompt: Optional[str] = None  # 搜索爬虫的tag列表，以 `,` 分割
