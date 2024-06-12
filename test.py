from fastapi import FastAPI
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
import random
import os, sys
app = FastAPI()

IMAGES = os.listdir("./images")[1:]

@app.get("/image/{image_name}")
async def get_image(image_name: str):
    img_path = 'images/' + image_name
    return FileResponse(img_path, media_type="image/jpeg")

@app.get('/')
async def rand_image():
    return RedirectResponse('/image/' + random.choice(IMAGES), status_code=302)