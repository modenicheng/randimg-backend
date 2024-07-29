from icecream import ic
from db import crud
from . import downloader, utils, configs, manager, uploader, collector, processor

path = configs.IMAGE_DIR

if __name__ == '__main__':
    c = manager.FollowingUserCrawlerManager(69776150)
    c.crawl()