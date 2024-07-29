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
    p = requests.api.patch(configs.SERVER + 'image/' + str(image_id),
                       headers=configs.HEADERS,
                       json=data)
    p.close()
    print(f'Start to process image {image_id}')
    res = requests.api.get(configs.SERVER + 'image/' + str(image_id),
                           params={'local': 'true'},
                           stream=True,
                           headers=configs.HEADERS)
    try:
        assert res.status_code == 200
    except AssertionError as e:
        data = {'id': image_id, 'processing': False, 'processed': False}
        print(f'Failed to fetch image {image_id}, {res.status_code} \n {res.content}')
        requests.api.post(configs.SERVER + 'crawler/image',
                           headers=configs.HEADERS,
                           json=data)
        return
    finally:
        res.close()
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
    p = requests.api.patch(configs.SERVER + '/image/' + str(image_id),
                       headers=configs.HEADERS,
                       json=data)
    p.close()
    del image, p
    print(f'Seccessfully processed image {image_id}')
def loop():
    while True:
        try:
            worker()
        except Exception as e:
            print('Error in worker', e)
