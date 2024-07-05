from spider import PixivUserCrawler
from icecream import ic
from concurrent.futures import ThreadPoolExecutor



from db import crud

ids = [4635318, 31344433, 33718285, 3438728, 53684744, 9631509, 211515, 66326024, 18996571, 28771714, 58338, 1113943, 3728296, 34054962, 8036174, 2396642, 15611520]
def c(id) :
    crawler = PixivUserCrawler(id)
    crawler.crawl()
    
if __name__ == "__main__" :   
    for i in ids:
        c(i)