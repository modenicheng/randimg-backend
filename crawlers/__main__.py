from icecream import ic

from . import downloader, utils, configs, manager, uploader, collector, processor

path = configs.IMAGE_DIR

if __name__ == '__main__':
    c = manager.UserCrawlerManager(40671335)
    c.crawl()