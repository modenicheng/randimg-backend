from icecream import ic
from db import crud
from . import downloader, utils, configs, manager, uploader, collector, processor

path = configs.IMAGE_DIR

if __name__ == '__main__':
    # ic(collector.pixiv_user_collector(3728296))
    d1 = {
        'author': {
            'name': 'さねよし',
            'platform': 'pixiv',
            'platform_id': 3728296
        },
        'id': 5380613,
        'tags': [{
            'name': 'オリジナル',
            'translated_name': '原创'
        }],
        'title': '無題'
    }
    ic(collector.pixiv_illusts_collector(d1))
    d2 = {
        'aspect_ratio': 1.0526315789473684,
        'author': {
            'name': 'さねよし',
            'platform': 'pixiv',
            'platform_id': 3728296
        },
        'height': 760,
        'id': 5380613,
        'image_path': '5380613_p0.jpg',
        'image_url':
        'https://i.pximg.net/img-original/img/2009/07/29/20/39/22/5380613_p0.jpg',
        'tags': [{
            'name': 'オリジナル',
            'translated_name': '原创'
        }],
        'title': '無題',
        'url':
        'https://i.pximg.net/img-original/img/2009/07/29/20/39/22/5380613_p0.jpg',
        'width': 800
    }
    ic(downloader.download_pixiv_image_file(d2))
    ic(
        uploader.upload_image_file(configs.IMAGE_DIR + d2['image_path'],
                                   d2['image_path']))
    ic(crud.is_image_processed(d2['image_path']))
    processor.process_image(d2)