from . import configs, utils
import requests
from icecream import ic
from PIL import Image
from io import BytesIO
from time import sleep
import random
def worker():
    sleep(random.random())
    res = requests.api.get(configs.SERVER + 'crawler/image',
                           headers=configs.HEADERS)
    if res.status_code == 200:
        if res.json() == []:
            return
        image_id = res.json()['id']
        image_path = res.json()['image_path']
    else:
        return
    data = {
        'id': image_id,
        'image_path': image_path,
        "processed": False,
        "processing": True,
    }
    requests.api.patch(configs.SERVER + '/image/' + str(image_id),
                           headers=configs.HEADERS,
                           json=data)
    print(f'Start to process image {image_id}')
    res = requests.api.get(configs.SERVER + 'image/' + str(image_id),
                           params={'local': 'true'},
                           stream=True,
                           headers=configs.HEADERS)
    assert res.status_code == 200
    image = Image.open(BytesIO(res.content)).convert('RGB')
    colors, primary = utils.extract_theme_colors(image, scale=0.3)
    data = {
        'id': image_id,
        'image_path': image_path,
        'colors': {
            'colors': colors,
            'primary_color': primary
        },
        "processed": True,
        "processing": False,
    }
    requests.api.patch(configs.SERVER + '/image/' + str(image_id),
                           headers=configs.HEADERS,
                           json=data)
    del image
    print(f'Seccessfully processed image {image_id}')
    
def loop():
    while True:
        try:
            worker()
        except Exception as e:
            print('Error in worker', e)