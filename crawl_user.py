from crawlers import manager

if __name__ == "__main__":

    ids = input('Input Ids ( split by comma ) > ').split(',')
    for i in ids:
        crawler = manager.UserCrawlerManager(i)
        crawler.crawl()
        del crawler