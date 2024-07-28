from icecream import ic
from db import crud
from . import downloader, utils, configs, manager, uploader, collector, processor

path = configs.IMAGE_DIR

if __name__ == '__main__':
    manager.FollowingUserCrawlerManager(108335841)