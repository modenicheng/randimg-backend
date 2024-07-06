from icecream import ic

from . import downloader, utils, configs, uploader, collector, processor

path = configs.IMAGE_DIR

if __name__ == '__main__':
    # illusts = collector.pixiv_user_collector(40671335)
    # data = []
    # for illust in illusts[:5]:
    #     images = collector.pixiv_illusts_collector(illust)
    #     ic(images)
    #     data.extend(images)
    # downloader.download_pixiv_image_file('https://i.pximg.net/img-original/img/2023/12/31/13/39/45/114721798_p0.jpg')
    d = processor.process_image({
        'author': {
            'name': '极夜繁声',
            'platform': 'pixiv',
            'platform_id': 40671335
        },
        'height':
        3137,
        'id':
        114721798,
        'image_path':
        '114721798_p0.jpg',
        'tags': [{
            'name': '鍾離',
            'translated_name': '钟离'
        }, {
            'name': '插画',
            'translated_name': 'illustration'
        }, {
            'name': '原神',
            'translated_name': 'Genshin Impact'
        }, {
            'name': 'お誕生日おめでとうございます',
            'translated_name': 'happy birthday'
        }],
        'title':
        '生日快乐！',
        'url':
        'https://i.pximg.net/img-original/img/2023/12/31/13/39/45/114721798_p0.jpg',
        'width':
        2271
    })
    ic(d)
