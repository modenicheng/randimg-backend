from spider import PixivUserCrawler
from icecream import ic


from db import crud
crawler = PixivUserCrawler(420509)
crawler.crawl()