import requests
from cache import cache
from . import Downloader, configs, utils
from time import sleep
from typing import Literal
import datetime
import tqdm
import re
from icecream import ic

from db import crud

import threading
import multiprocessing
import queue

import dogecloud
from dogecloud import oss

import logging


class RankingCrawler:

    def __init__(self,
                 mode: Literal["daily", "weekly", "monthly", "male", "female",
                               "daily_ai", "daily_r18", "weekly_r18",
                               "male_r18", "female_r18", "daily_r18_ai"],
                 content_mode: Literal['all', 'illust', "manga", "ugoira"],
                 start_date: datetime.date, ranges: int, pages: int):

        self.mode = mode
        self.content_mode = content_mode
        self.start_date = start_date
        self.range = ranges
        self.pages = pages
        self.date = start_date

        self.task_queue = multiprocessing.JoinableQueue()
        self.result_queue = multiprocessing.Queue()
        self.pbar: tqdm.tqdm | None = None

        self.url_template = "https://www.pixiv.net/ranking.php?" + "&".join([
            f"mode={self.mode}",
            f"content={self.content_mode}",
            "date={}",
            "p={}",
            "format=json",
        ])

        self.upload_retry = 0
        self.finished = 0

    def collect_ranking_list(self):
        url_list = []

        date = self.date

        while date < datetime.date.today():
            for i in range(self.pages):
                ranking_list_url = self.url_template.format(
                    date.strftime("%Y%m%d"), i + 1)
                url_list.append(ranking_list_url)
            date += datetime.timedelta(1)

        self.url_list = url_list

        data = []
        for url in url_list:
            headers = {
                "Referer": re.search("(.*)&p", url).group(1),
                **configs.HEADERS
            }
            res = requests.api.get(url,
                                   headers=headers,
                                   proxies=configs.PROXIES)
            if res.status_code == 200:
                contents = res.json()['contents']
                data += contents  # add each batch of data into a list

        self.data = data
        return data

    def crawl(self):
        self.collect_ranking_list()
        for entry in self.data:
            if entry['user_id'] in configs.ARTISTS_BLACKLIST:
                pass
            elif entry['illust_id'] in crud.get_illust_ids():
                print(f'skip {entry["illust_id"]}')
            else:
                self.task_queue.put(entry)

        processes: list[multiprocessing.Process] = []

        for _ in range(configs.IMAGE_DOWNLOAD_THREADS):
            p = multiprocessing.Process(target=self.worker)
            processes.append(p)
            p.start()

        self.task_queue.join()
        results = []
        while not self.result_queue.empty():
            results.append(self.result_queue.get())

        # 停止所有进程
        for p in processes:
            p.terminate()
            p.join()

        return results

    def worker(self):
        while not self.task_queue.empty():
            try:
                entry = self.task_queue.get()
                illust_id = int(entry['illust_id'])
                image_list = Downloader.pixiv_artwork_page_image_list(
                    illust_id)

                for image in image_list:
                    image_url = image['image_url']
                    image_blob = Downloader.pixiv_image_blob(image_url)
                    image_path = re.search(r'/([0-9]*_p[0-9]*\..*)',
                                           image['image_url']).group(1)

                    sorted_colors, main_color = utils.extract_theme_colors(
                        image_blob, scale=0.7)

                    t = threading.Thread(target=self.upload_image,
                                         args=(image_blob, image_path))
                    t.start()

                    db_data = {
                        'title': entry['title'],
                        'image_path': image_path,
                        'source_id': entry['illust_id'],
                        'source_url':
                        f"https://www.pixiv.net/artworks/{entry['illust_id']}",  # this is the link to the original page of the Pixiv site
                        'width': image['width'],
                        'height': image['height'],
                        'aspect_ratio': image['aspect_ratio'],
                        'tags': entry['tags'],
                        'author': {
                            'platform': 'pixiv',
                            'platform_id': entry['user_id'],
                            'homepage':
                            f'https://www.pixiv.net/users/{entry["user_id"]}',
                            'name': entry['user_name']
                        },
                        'color': {
                            'color_primary': main_color,
                            'color_series': sorted_colors
                        }
                    }
                    crud.create_image(db_data)
                print(f'Image info of {image_path} stored in db')

            except:
                pass

    def upload_image(self, image_blob, image_uri: str):
        if self.upload_retry >= configs.MAX_UPLOAD_RETRY:
            return -1
        storage = oss.OSS()
        try:
            storage.upload_image_blob(image_blob, image_uri)
            print(f'Image {image_uri} uploaded')

        except:
            self.upload_retry += 1
            sleep(5)
            self.upload_image(image_blob, image_uri)


class RankingCrawler_Rebuild:

    def __init__(self,
                 mode: Literal["daily", "weekly", "monthly", "male", "female",
                               "daily_ai", "daily_r18", "weekly_r18",
                               "male_r18", "female_r18", "daily_r18_ai"],
                 content_mode: Literal['all', 'illust', "manga", "ugoira"],
                 start_date: datetime.date, ranges: int, pages: int):

        self.mode = mode
        self.content_mode = content_mode
        self.start_date = start_date
        self.range = ranges
        self.pages = pages
        self.date = start_date

        self.pbar: tqdm.tqdm | None = None

        self.ranking_list_url = "https://www.pixiv.net/ranking.php?" + "&".join(
            [
                f"mode={self.mode}",
                f"content={self.content_mode}",
                "date={}",
                "p={}",
                "format=json",
            ])

        self.quit_flag = False

    def collect_ranking_list(self):
        url_list = []
        date = self.date
        page_list_queue = queue.Queue()
        while date < datetime.date.today():
            for i in range(self.pages):
                ranking_list_url = self.ranking_list_url.format(
                    date.strftime("%Y%m%d"), i + 1)
                url_list.append(ranking_list_url)
            date += datetime.timedelta(1)
        self.url_list = url_list

        data = []
        for url in url_list:
            headers = {
                "Referer": re.search("(.*)&p", url).group(1),
                **configs.HEADERS
            }
            res = requests.api.get(url,
                                   headers=headers,
                                   proxies=configs.PROXIES)
            if res.status_code == 200:
                contents = res.json()['contents']
                data += contents  # add each batch of data into a list

        self.data = data
        return data

    def get_image_list(self, page_list_queue) -> list[dict]:
        image_list_queue = queue.Queue()

        for i in range(configs.GET_PAGE_THREADS):
            t = threading.Thread(target=self.get_illust_detail,
                                 args=(page_list_queue, image_list_queue),
                                 name=f'THREAD illust_detail {i}')
            t.start()

    def get_illust_detail(
        self,
        page_list_queue: queue.Queue,
        image_list_queue: queue.Queue,
    ):
        while not self.quit_flag:
            illust_page_id = int(page_list_queue.get()['illust_id'])
            print(
                f'{threading.current_thread()} | Getting image list of illust_id {illust_page_id}'
            )
            image_list = Downloader.pixiv_artwork_page_image_list(
                illust_page_id)
            for image in image_list:
                image_list_queue.put(image)
        page_list_queue.task_done()

    def download_images(self, image_list_queue: queue.Queue,
                        image_upload_queue: queue.Queue):
        while not self.quit_flag:
            image = image_list_queue.get()
            print(
                f'{threading.current_thread()} | Downloading image {image["image_id"]}'
            )
            image_blob = Downloader.pixiv_image_blob(image['image_id'])
            image_upload_queue.put({
                'image_id': image['image_id'],
                'image_blob': image_blob
            })


class UserCrawler:
    """
    Collect all artworks from a single artist

    Sample URL: "https://www.pixiv.net/ajax/user/23945843/profile/all?lang=zh"
    """

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        self.url = f"https://www.pixiv.net/ajax/user/{user_id}/profile/all?lang=zh"
        # self.url = f"https://www.pixiv.net/users/{self.user_id}/illustrations"
        self.headers = {
            "Referer": f"https://www.pixiv.net/users/{user_id}/illustrations",
            **configs.HEADERS
        }

    def collect(self) -> list:
        res = requests.get(self.url,
                           headers=self.headers,
                           proxies=configs.PROXIES)
        if res.status_code == 200:
            id_dict: dict = res.json()['body']['illusts']
            id_list = list(id_dict.keys())
            return id_list
        else:
            sleep(3)
            return self.collect()

    def get_illust_detail(self, illust_id: int) -> dict:
        url = f"https://www.pixiv.net/ajax/illust/{illust_id}/pages?lang=zh"
        res = requests.get(url, headers=self.headers, proxies=configs.PROXIES)
        if res.status_code == 200:
            data = res.json()['body']
            return [{
                'height': image['height'],
                'width': image['width'],
                'url': image['urls']['original']
            } for image in data]
        else:
            sleep(3)
            return self.get_illust_detail(illust_id)


## 快点REMAKE吧…… 找到新的库了
## pixivpy-async: https://github.com/Mikubill/pixivpy-async

from pixivpy3 import *
from concurrent.futures import ThreadPoolExecutor, as_completed

l = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PixivCrawlerBase:
    def __init__(self, user_id: int | str) -> None:
        self.api = ByPassSniApi()
        self.api.require_appapi_hosts()
        self.api.set_accept_language('zh-CN')
        self.api.auth(refresh_token=self.get_token())
        self.storage = oss.OSS()
        
    def get_token(self):
        current = cache.get('pixiv_refresh_token')
        prev = cache.get('pixiv_refresh_token_prev')
        if current:
            return current
        elif prev:
            new = self.api.refresh_token
            cache.set('pixiv_refresh_token', new, expire=3000)
            cache.set('pixiv_refresh_token_prev', new, expire=3600)
            return new
        else:
            new = input("pixiv refresh token: ")
            cache.set('pixiv_refresh_token', new, expire=3000)
            cache.set('pixiv_refresh_token_prev', new, expire=3600)
            return new

class PixivUserCrawler:

    def __init__(self, user_id: int | str) -> None:
        self.api = ByPassSniApi()
        self.api.require_appapi_hosts()
        self.api.set_accept_language('zh-CN')
        self.api.auth(refresh_token=self.get_token())
        self.user_id = user_id
        self.image_queue = queue.Queue()
        self.storage = oss.OSS()

    def get_token(self):
        current = cache.get('pixiv_refresh_token')
        prev = cache.get('pixiv_refresh_token_prev')
        if current:
            return current
        elif prev:
            new = self.api.refresh_token
            cache.set('pixiv_refresh_token', new, expire=3000)
            cache.set('pixiv_refresh_token_prev', new, expire=3600)
            return new
        else:
            new = input("pixiv refresh token: ")
            cache.set('pixiv_refresh_token', new, expire=3000)
            cache.set('pixiv_refresh_token_prev', new, expire=3600)
            return new

    def collect_illusts_list(self):
        l.info(f"Collecting illusts list of user {self.user_id}")
        illusts_json = self.api.user_illusts(self.user_id)
        illusts = [{
            "id": item['id'],
            "title": item['title'],
            "tags": item['tags'],
            "author": {
                "name":
                self.api.user_detail(item['user']['id'])['user']['name'],
                "platform_id": item['user']['id'],
                "platform": "pixiv",
            }
        } for item in illusts_json['illusts']]
        l.info(f'Done. Total illusts: {len(illusts)}')
        return illusts

    def download_illust(self, illust):
        l.info(f'{threading.current_thread().name} | Downloading illust {illust["id"]}')
        images = Downloader.pixiv_artwork_page_image_list(illust['id'])
        for image in images:
            image_data = {**image, **illust}
            file_name = image_data['image_url'].split('/')[-1]
            image_blob = Downloader.pixiv_image_blob(image['image_url'])
            t1 = threading.Thread(
                target=self.dump_image(image_data, image_blob))
            t2 = threading.Thread(
                target=self.upload_image(image_blob, file_name))
            t1.start()
            t2.start()
            t1.join()

    def dump_image(self, image_data: dict, image_blob):
        colors, primary = utils.extract_theme_colors(image_blob)
        data = {
            **image_data,
            "colors": {
                "primary_color": primary,
                "colors": colors
            },
        }
        crud.create_image_rebuild(data)

    def upload_image(self, image_blob, image_uri: str):
        l.info(f'Uploading {image_uri}')
        self.storage.upload_image_blob(image_blob, image_uri)
        crud.uploaded_image(image_uri)
        l.info(f'Image {image_uri} uploaded')

    def crawl(self):
        illusts = self.collect_illusts_list()
        with ThreadPoolExecutor(
                max_workers=configs.IMAGE_DOWNLOAD_THREADS) as pool:
            _ = [
                pool.submit(self.download_illust, illust) for illust in illusts
            ]
