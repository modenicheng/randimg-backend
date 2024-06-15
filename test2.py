from icecream import ic

import datetime
from spider import *

test_entry = {
    "title": "ススス",
    "date": "2024年06月13日 10:59",
    "tags":
    ["崩壊:スターレイル", "HonkaiStarRail", "ヘルタ", "判官姉妹", "崩壊:スターレイル1000users入り"],
    "url":
    "https://i.pximg.net/c/240x480/img-master/img/2024/06/13/10/59/34/119594240_p0_master1200.jpg",
    "illust_type": "0",
    "illust_book_style": "0",
    "illust_page_count": "4",
    "user_name": "COCOball",
    "profile_img":
    "https://i.pximg.net/user-profile/img/2023/10/16/08/23/39/25053980_0c03a35f449f71ed83b855533e6f6a24_50.jpg",
    "illust_id": 119594240,
    "width": 2577,
    "height": 3624,
    "user_id": 31383108,
    "rank": 14,
    "yes_rank": 24,
    "rating_count": 377,
    "view_count": 5530,
    "illust_upload_timestamp": 1718243974,
}

if __name__ == '__main__':
    multiprocessing.freeze_support()
    crl = RankingCrawler('daily', 'illust', datetime.date(2024, 6, 12), 5, 3)
    crl.task_queue.put(test_entry)
    crl.data = []

    crl.crawl()

# from db import crud

# randdata = crud.generate_random_data()

# crud.create_image(randdata)
