from spider import RankingCrawler
import datetime
import json
import multiprocessing

if __name__ == '__main__':
    multiprocessing.freeze_support()

    rkc = RankingCrawler('daily', 'illust', datetime.date(2024, 6, 10), 3, 2)
    result = rkc.crawl()

    try:
        with open('log.txt', 'w') as f:
            f.write(json.dumps(result))
    finally:
        print(result)
