from fastapi import FastAPI, Body, Depends, status, Header
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
from typing import Union

from fastapi.exceptions import HTTPException
import random
import os, sys
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn
import json
from typing import Annotated, Union
from pydantic import BaseModel, Field
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
    ic(token)
    try:
        user = get_current_user(token)
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
def get_image(image_id: int, format: str = 'json'):
    data: schemas.ImageSchema = crud.get_image_by_id(image_id)
    if data == None:
        return JSONResponse(content={'error': 'image not found'},
                            status_code=404)
    if format == 'json':
        del data.uploaded, data.accessable
        data.colors = json.loads(data.colors)
        return data
    elif format == 'image':
        return RedirectResponse(url=CDN_BASE_URL + data.image_path,
                                status_code=307)


@app.get('/')
def rand_image(format: str = 'json',
               ratio_floor: float = 0,
               ratio_ceil: float = 10,
               tags=''):
    with get_db() as db:
        if tags:
            tags = tags.split(',')
            image_list = db.query(models.Image).\
                join(models.Image.tags).\
                filter(
                    models.Image.accessable == True,
                    models.Image.aspect_ratio > ratio_floor,
                    models.Image.aspect_ratio < ratio_ceil,
                    models.Tag.name.in_(tags)
                ).all()
        else:
            image_list = db.query(models.Image).\
                filter(
                    models.Image.accessable == True,
                    models.Image.aspect_ratio > ratio_floor,
                    models.Image.aspect_ratio < ratio_ceil
                ).all()
        if len(image_list) == 0: return Exception('No image found')
        else:
            ic(len(image_list))
            img = random.choice(image_list)

        if format == 'json':
            data = crud.get_image_by_id(img.id).__dict__
            data['colors'] = json.loads(img.colors)
            data['src'] = CDN_BASE_URL + img.image_path
            del data['uploaded'], data['accessable'], data['image_path']
            return data
        elif format == 'image':
            ic(img.id)
            return RedirectResponse(url=CDN_BASE_URL + img.image_path,
                                    status_code=307)


@app.get('/list')
def get_image_list(authorization: Annotated[str, Header()] = None,
                   offset: int = 0,
                   limit: int = 30):
    if limit >= 300: limit = 100
    if offset < 0: offset = 0
    if limit < 0: limit = 0
    
    # 如果带有验证，则验证通过后返回全部图片，如果无验证则只返回accessable=true的图片
    if authorization:
        token = authorization.split(' ')[1]
        if auth(token):
            return crud.get_image_list(offset=offset,
                                       limit=limit,
                                       accessable=True,
                                       more_data=True)
    else:
        return crud.get_image_list(
            offset=offset,
            limit=limit,
        )


@app.patch('/list')
def update_images(images: list[schemas.ImageManagementSchema]):
    with get_db() as db:
        try:
            results = [crud.update_image(image, db) for image in images]
            return results
        except Exception as e:
            ic(e)
            raise HTTPException(status_code=400, detail=str(e))


@app.patch('/image/{image_id}')
def update_image(image_id: int, image: schemas.ImageManagementSchema,
                 token: Annotated[str, Depends(oauth2_scheme)]):
    update_data = image.model_dump(exclude_unset=True)
    with get_db() as db:
        image_orm = crud.update_image(update_data, db)
        return image_orm


@app.delete('/image/{image_id}')
def del_image(image_id: int):
    pass


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
