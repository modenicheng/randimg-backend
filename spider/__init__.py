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
                image_list = Downloader.pixiv_artwork_page_image_list(illust_id)

                for image in image_list:
                    image_url = image['image_url']
                    image_blob = Downloader.pixiv_image_blob(image_url)
                    image_path = re.search(r'/([0-9]*_p[0-9]*\..*)',
                                    image['image_url']).group(1)

                    sorted_colors, main_color = utils.extract_theme_colors(
                        image_blob, scale=0.7)
                    
                    t = threading.Thread(target=self.upload_image, args=(image_blob, image_path))
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

        self.ranking_list_url = "https://www.pixiv.net/ranking.php?" + "&".join([
            f"mode={self.mode}",
            f"content={self.content_mode}",
            "date={}",
            "p={}",
            "format=json",
        ])
        
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
            t = threading.Thread(target=self.get_illust_detail, args=(page_list_queue, image_list_queue), name=f'THREAD illust_detail {i}')
            t.start()
        image_list_queue.join()
    
    def get_illust_detail(self, page_list_queue: queue.Queue, image_list_queue: queue.Queue, ):
        while not page_list_queue.empty():
            illust_page_id = int(page_list_queue.get()['illust_id'])
            print(f'{threading.current_thread()} | Getting image list of illust_id {illust_page_id}')
            image_list = Downloader.pixiv_artwork_page_image_list(illust_page_id)
            for image in image_list:
                image_list_queue.put(image)
        page_list_queue.task_done()
        return image_list_queue
        
    