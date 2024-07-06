from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed, wait
import threading
from . import configs, collector, uploader, downloader, processor


class Manager:

    def __init__(self) -> None:
        self.collector_pool = ThreadPoolExecutor(
            max_workers=configs.COLLECTOR_NUM)
        self.downloader_pool = ThreadPoolExecutor(
            max_workers=configs.DOWNLOADER_NUM)
        self.uploader_pool = ThreadPoolExecutor(
            max_workers=configs.UPLOADER_NUM)
        self.processor_pool = ProcessPoolExecutor(
            max_workers=configs.PROCESSOR_NUM)


class UserCrawlerManager:

    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id

    def crawl(self) -> None:
        illusts = collector.pixiv_user_collector(self.user_id)
        print(f'Start to crawl {self.user_id}')
        with ThreadPoolExecutor(
                max_workers=configs.COLLECTOR_NUM) as collector_pool:
            collect_tasks = [
                collector_pool.submit(collector.pixiv_illusts_collector,
                                      illust) for illust in illusts
            ]

            collected_list = [
                future.result() for future in as_completed(collect_tasks)
            ]

        images = []
        for i in collected_list:
            images.extend(i)

        with ThreadPoolExecutor(
                max_workers=configs.DOWNLOADER_NUM) as downloader_pool:
            download_tasks = [
                downloader_pool.submit(downloader.download_pixiv_image_file,
                                       illust) for illust in images
            ]

            downloaded_list = [
                future.result() for future in as_completed(download_tasks)
            ]

        with ThreadPoolExecutor(
                max_workers=configs.PROCESSOR_NUM) as processor_pool:
            process_tasks = [
                processor_pool.submit(processor.process_image, image)
                for image in downloaded_list
            ]
            
            for i in as_completed(process_tasks):
                print(i)
            
            
            
            
