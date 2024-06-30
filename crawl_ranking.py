from spider import RankingCrawler
import datetime
import json
import multiprocessing

from icecream import ic

ic.disable()

if __name__ == '__main__':
    multiprocessing.freeze_support()

    rkc = RankingCrawler('daily', 'illust', datetime.date(2024, 5, 20), 20, 2)
    result = rkc.crawl()
