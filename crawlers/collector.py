import requests
from . import configs
from time import sleep
from pixivpy3 import AppPixivAPI, ByPassSniApi
import json
from datetime import datetime, timedelta
from icecream import ic
from typing import Literal
import re


def ranking_list_collector(type: Literal['all', 'illust', "manga",
                                         "ugoira"] = 'illust'):
    aapi = AppPixivAPI()
    aapi.set_accept_language("zh-cn")
    aapi.auth(refresh_token=configs.REFRESH_TOKEN)
    json_result = aapi.illust_ranking(
        "day", date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"))
    ic(json_result["illusts"][0])

def pixiv_user_collector(user_id: int):
    next_qs = False
    aapi = ByPassSniApi()
    aapi.require_appapi_hosts()
    aapi.set_accept_language("zh-cn")
    aapi.auth(refresh_token=configs.REFRESH_TOKEN)
    username = aapi.user_detail(user_id)['user']['name']
    json_response = aapi.user_illusts(user_id)
    illusts: list = json_response['illusts']
    next_qs = aapi.parse_qs(json_response.next_url)
    while next_qs:
        print("Requesting next page")
        res = aapi.user_illusts(**next_qs)
        illusts.extend(res['illusts'])
        if res['next_url']:
            next_qs = aapi.parse_qs(res['next_url'])
        else:
            next_qs = False
    for _ in range(20):
        try:
            data = [{
                "id": item['id'],
                "title": item['title'],
                "tags": item['tags'],
                "author": {
                    "name": username,
                    "platform_id": item['user']['id'],
                    "platform": "pixiv",
                }
            } for item in illusts]
            print(f'Done. Total illusts: {len(data)}')
            return data
        except KeyError as e:
            print(e)
            print("Reach the speed limit. wait for 20s to retry.")
            sleep(20)


def pixiv_illusts_collector(illust: dict):
    try:
        illust_id = str(illust['id'])
    except KeyError:
        print("Illust dict not valid")
        return
    url = f"https://www.pixiv.net/ajax/illust/{illust_id}/pages?lang=zh"
    try:
        print(f"Requesting image list of {illust_id}")
        res = requests.get(url,
                           headers={
                               "Referer":
                               f"https://www.pixiv.net/artworks/{illust_id}",
                               **configs.HEADERS
                           },
                           proxies=configs.PROXIES)
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f"Request {illust_id} failed. Retrying...\nERROR: {e}")
        sleep(5)
        return pixiv_illusts_collector(illust_id)

    if res.status_code == 200:
        data = res.json()['body']
        return [{
            'height': image['height'],
            'width': image['width'],
            'aspect_ratio': image['width'] / image['height'],
            'url': image['urls']['original'],
            'image_path': image['urls']['original'].split('/')[-1],
            **illust
        } for image in data]
    else:
        sleep(3)
        return pixiv_illusts_collector(illust_id)
