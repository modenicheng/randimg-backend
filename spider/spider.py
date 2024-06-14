import requests
import json
import datetime
from typing import Literal

from db.schemas import ImageSchema, TagSchema, AuthorSchema
from db.models import Image, Tag, Author
from db.database import SessionLocal
from sqlalchemy.orm import Session

from icecream import ic


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Note:
# 各个镜像站的图片id貌似均保持一致，所以可以借助id来判定是否已经爬取过


class SpiderBase:

    def __init__(self):
        self.db: Session = get_db()
        self.base_url = ''
        self.headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua":
            "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site"
        }


class Pixiviz(SpiderBase):

    def __init__(self):
        super().__init__()
        self.base_url = "https://pixiviz-api-rn.pwp.link/v1/"

    def get_rank(self,
                 page=1,
                 mode: Literal['day', 'week', 'month'] = 'day',
                 date=str(datetime.date.today())):
        url = self.base_url + f"illust/rank?mode={mode}&page={page}&date={date}"
        res = requests.get(url, headers=self.headers)
        ic(url)
        ic(res.status_code)

class Vilipix(SpiderBase):
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.vilipix.com/api/v1/"
        
    def get_rank_list(self,
                 offset=0,
                 limit=30,
                 mode: Literal['day', 'week', 'month'] = 'day',
                 date=str(datetime.date.today().strftime('%Y%m%d'))):
        
        mode_index = 0 if mode == 'day' else 1 if mode == 'week' else 2
        res = requests.get(self.base_url + 'picture/ranking', {
            'offset': offset,
            'limit': limit,
            'mode': mode_index,
            'ranking_date': date
        })
        
        if res.status_code != 200:
            print(res.status_code, res.text)
            return 
        
        data = res.json()
        rows = data['data']['rows']
        count = data['data']['count']
        
        while len(rows) < count:
            offset += limit
            res = requests.get(self.base_url + 'picture/ranking', {
                'offset': offset,
                'limit': limit,
                'mode': mode_index,
                'ranking_date': date
            })
            if res.status_code != 200:
                print(res.status_code, res.text)
                return 
            
            data = res.json()
            rows += data['data']['rows']
            
        self.rows = rows
        return rows
    
    