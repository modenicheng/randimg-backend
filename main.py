from fastapi import FastAPI, Body, Depends, status, Header, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    ORJSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
    UJSONResponse,
)
from datetime import datetime, timedelta, timezone
from typing import Union, Literal
import crawlers
from fastapi.exceptions import HTTPException
import random
import os, sys
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn
import json
from typing import Annotated, Union
from pydantic import BaseModel, Field
import crawlers.manager
from db import crud, models, schemas
from db.crud import get_db
from icecream import ic
from db.schemas import AdminSchema
from sqlalchemy.orm import Session
from jose import jwt
from jose.exceptions import JWEInvalidAuth, ExpiredSignatureError

from passlib.context import CryptContext

from configs import *

from fastapi.middleware.cors import CORSMiddleware
import queue
from collections import deque

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenData(BaseModel):
    username: Union[str, None] = None


class Token(BaseModel):
    access_token: str
    token_type: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    user = get_admin(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def decode_token(token: str) -> AdminSchema:
    ic(token)
    with get_db() as db:
        admin = db.query(
            models.Admin).filter(models.Admin.username == token).first()
        if admin == None:
            raise Exception('admin not found')
        return admin


def get_admin(username: str):
    with get_db() as db:
        admin: schemas.AdminSchema = db.query(
            models.Admin).filter(models.Admin.username == username).first()
        return admin


def create_access_token(data: dict,
                        expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username == '':
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWEInvalidAuth:
        raise credentials_exception
    user = get_admin(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def auth(token: str = ''):
    try:
        get_current_user(token)
        return True
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail='token expired')


@app.post("/token")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), ) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username},
                                       expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@app.get("/image/{image_id}")
def get_image(image_id: int,
              format: str = 'json',
              local: bool = False,
              authorization: Annotated[str, Header()] = None):
    if authorization:
        token = authorization.split(' ')[1]
        if auth(token):
            is_admin = True
        else:
            raise HTTPException(status_code=401)
    data: dict | None = crud.get_image_by_id(image_id, is_admin=is_admin)
    if data == None:
        return JSONResponse(content={'error': 'image not found'},
                            status_code=404)
    if local == True:
        try:
            return FileResponse('./images/' + data.get('image_path'))
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail='image not found')
        except:
            raise HTTPException(status_code=404, detail='image not found')
    if format == 'json':
        return data
    elif format == 'image':
        return RedirectResponse(url=data['src'], status_code=307)


@app.get('/')
def rand_image(format: str = 'json',
               ratio_floor: float = 0,
               ratio_ceil: float = 10,
               tags=None):
    image_list = crud.get_image_list(ratio_ceil=ratio_ceil,
                                     ratio_floor=ratio_floor,
                                     full_list=True,
                                     accessable=True,
                                     tags=tags,
                                     only_ids=True)
    if len(image_list) == 0:
        raise HTTPException(status_code=404, detail='No image found')
    else:
        img_id = random.choice(image_list)
        img = crud.get_image_by_id(img_id)

    if format == 'json':
        return img
    elif format == 'image':
        return RedirectResponse(url=img['src'], status_code=307)


@app.get('/list')
def get_image_list(authorization: Annotated[str, Header()] = None,
                   offset: int = 0,
                   limit: int = 30,
                   desc: bool | str = True,
                   ratio_floor: float = 0,
                   ratio_ceil: float = 10,
                   author: str | int = None,
                   accessable: Literal['True', 'False', 'all', 'true',
                                       'false'] = 'all',
                   tags=None):
    if limit >= 300: limit = 100
    if offset < 0: offset = 0
    if limit < 0: limit = 0
    accessable = 'all' if accessable == 'all' else True if accessable.lower(
    ) == 'true' else False
    try:
        desc = True if desc.lower() == 'true' else False
    except:
        pass
    try:
        author = int(author)
    except:
        pass
    # 如果带有验证，则验证通过后返回全部已上传图片，如果无验证则只返回accessable=true的图片
    if authorization:
        token = authorization.split(' ')[1]
        if auth(token):
            return crud.get_image_list(offset=offset,
                                       limit=limit,
                                       more_data=True,
                                       accessable=accessable,
                                       desc=desc,
                                       ratio_ceil=ratio_ceil,
                                       ratio_floor=ratio_floor,
                                       author=author,
                                       tags=tags)
    else:
        return crud.get_image_list(offset=offset,
                                   limit=limit,
                                   desc=desc,
                                   accessable=True,
                                   ratio_ceil=ratio_ceil,
                                   ratio_floor=ratio_floor,
                                   author=author,
                                   tags=tags)


@app.get('/tags')
async def get_tags():
    return crud.get_tags()


@app.patch('/image/{image_id}')
def update_image(image_id: int, image: schemas.ImageManagementSchema,
                 token: Annotated[str, Depends(oauth2_scheme)]):
    if auth(token):
        update_data = image.model_dump(exclude_unset=True)
        with get_db() as db:
            image_orm = crud.update_image(update_data, db)
            return image_orm
    else:
        raise HTTPException(401)


@app.delete('/image/{image_id}')
def del_image(image_id: int):
    pass


@app.get('/crawler')
async def get_crawler_status():
    pass


@app.post('/crawler')
def create_crawler(data: schemas.CreateCrawlerSchema):
    with get_db() as db:
        if data.crawl_type == models.CrawlerType.USER and data.target_user_id == None:
            raise HTTPException(status_code=400,
                                 detail="target_user_id is required")
        if data.crawl_type == models.CrawlerType.RANKING and (
                data.target_end_date == None
                or data.target_start_date == None):
            raise HTTPException(
                status_code=400,
                detail="target_end_date and target_start_date is required")
        crawler = crud.create_crawler(data, db)
        return crawler


process_queue = deque()


@app.get('/crawler/image')
def get_unprocessed_images_list(token: Annotated[str,
                                                 Depends(oauth2_scheme)],
                                init: bool = False):
    global process_queue
    
    if auth(token):
        if init:
            images = crud.get_unprocessed_images(ids=True)
            process_queue = deque()
            [process_queue.append(i) for i in images]
            ic(process_queue.__len__())

            return {'status': 'ok', 'count': process_queue.__len__()}
        else:

            try:
                image = process_queue.pop()
                with get_db() as db:
                    crud.update_image({**image, 'processing': True}, db)
                    
                return image
            except Exception as e:
                ic(e)
                raise HTTPException(
                    status_code=404,
                    detail="No image found. Please try init first.")
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post('/crawler/image')
async def error_processing_image(token: Annotated[str, Depends(oauth2_scheme)],
                           request: Request):
    global process_queue
    with get_db() as db:
        try:
            data = await request.json()
            process_queue.appendleft(data.get('id'))
            return crud.update_image(data, db)
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=800)
