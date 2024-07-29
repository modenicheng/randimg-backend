from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed, wait
import threading
from . import configs, collector, uploader, downloader, processor
from multiprocessing import Pool
from icecream import ic
from typing import Literal


class Manager:

    def collect_illusts(self):
        collected_list = []
        return collected_list

    def collector_threads(self, illusts: list):
        with ThreadPoolExecutor(
                max_workers=configs.COLLECTOR_NUM) as collector_pool:
            collect_tasks = [
                collector_pool.submit(collector.pixiv_illusts_collector,
                                      illust) for illust in illusts
            ]
            del illusts

            collected_list = [
                future.result() for future in as_completed(collect_tasks)
            ]
        return collected_list

    def crawl(self) -> None:

        collected_list = self.collect_illusts()

        images = []
        for i in collected_list:
            images.extend(i)

        del collected_list

        with ThreadPoolExecutor(
                max_workers=configs.DOWNLOADER_NUM) as downloader_pool:
            download_tasks = [
                downloader_pool.submit(downloader.download_pixiv_image_file,
                                       illust) for illust in images
            ]
            del images

            downloaded_list = [
                future.result() for future in as_completed(download_tasks)
            ]

            del download_tasks

        with ThreadPoolExecutor(
                max_workers=configs.UPLOADER_NUM) as uploader_pool:
            uploaded_tasks = [
                uploader_pool.submit(uploader.upload_image_file,
                                     configs.IMAGE_DIR + '/' + i['image_path'],
                                     i['image_path']) for i in downloaded_list
            ]
            del downloaded_list, uploaded_tasks


class UserCrawlerManager(Manager):

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def collect_illusts(self):
        illusts = collector.pixiv_user_collector(self.user_id)
        collected_list = self.collector_threads(illusts)
        del illusts
        return collected_list


class BookmarkCrawlerManager(Manager):

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__()

    def collect_illusts(self):
        illusts = collector.pixiv_user_bookmarks_collector(self.user_id)
        collected_list = self.collector_threads(illusts)
        del illusts
        return collected_list


class RankingCrawlerManager(Manager):

    def __init__(self,
                 type: Literal['all', 'illust', "manga", "ugoira"] = 'illust'):
        pass

    def collect_illusts(self):
        pass


class FollowingUserCrawlerManager(Manager):

    def __init__(self, user_id: int | str) -> None:
        self.user_id = int(user_id)
        super().__init__()

    def collect_illusts(self):
        users = collector.following_users_collector(self.user_id)
        print(f"Total {len(users)} users to be crawled. \n {users}")
        with ThreadPoolExecutor(
                max_workers=2) as collector_pool:
            illusts_tasks = [
                collector_pool.submit(collector.pixiv_user_collector, user)
                for user in users
            ]
            del users
            ic(illusts_tasks)
            illusts = []
            for future in as_completed(illusts_tasks):
                illusts.extend(future.result())

        collected_list = self.collector_threads(illusts)
        del illusts
        return collected_list
