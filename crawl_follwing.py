from crawlers import manager

if __name__ == '__main__':
    user_id = input("your id >>")

    c = manager.FollowingUserCrawlerManager(user_id)
    c.crawl()