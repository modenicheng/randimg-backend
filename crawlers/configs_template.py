###########################
# Please copy configs_template.py to configs.py
###########################

# configs.py
import configs

IMAGE_DIR = configs.IMAGE_DIR
COLLECTOR_NUM = 10
DOWNLOADER_NUM = 10
UPLOADER_NUM = 10
PROCESSOR_NUM = 10
PROXIES = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

USER_ID = ''
COOKIE = ''
HEADERS = {
    "x-requested-with": "XMLHttpRequest",
    "COOKIE": COOKIE,
    "x-user-id": str(USER_ID),
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    'sec-ch-ua':
    '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Windows",
    'Accept':
    'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Dest': 'image',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}
ARTISTS_BLACKLIST = ['16776564', '11']
REFRESH_TOKEN = ""