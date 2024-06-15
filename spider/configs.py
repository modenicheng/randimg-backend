COOKIE = 'first_visit_datetime_pc=2024-05-06%2019%3A10%3A06; yuid_b=EzeVSQI; p_ab_id=1; p_ab_id_2=7; p_ab_d_id=1926764046; c_type=23; privacy_policy_notification=0; a_type=0; b_type=0; PHPSESSID=78789488_yFBwu6Cc5VxAKWHV1IAkr3FB0WSbejDW; device_token=7650548039bc6cc7395523280811e478; _ga_MZ1NL4PHH0=GS1.1.1718186396.2.0.1718186404.0.0.0; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; login_ever=yes; _gcl_au=1.1.2102363298.1718274302; privacy_policy_agreement=7; _gid=GA1.2.496373405.1718376742; cf_clearance=dalz1Dd9cXfmIfgTDusAr_oBNzqfKSmK6Ms_NvfaMeg-1718425847-1.0.1.1-_wHVAXafNpWwS6ecot2FdytS06RoCeK02CCLA.IrXI_2_HV6NZ6CVudKHlEwovtIAGBMzniGENuuYkGmZUTuSw; __cf_bm=h9vWuHx.xUZoTCU8DHJuKxHWFeTw31tVFT1t1ybPQ8s-1718442024-1.0.1.1-fJKTmWhJK.40T99q7RRAYi8fYpTRDJy.IjoRwdUuvklhK6c9aAm.FZL7mcS20KI6BmM0gJnGgmtxryiQr6.0ppFF.UH7GwmznXKkUFyDweI; _ga_75BBYNYN9J=GS1.1.1718442121.9.1.1718442545.0.0.0; _ga=GA1.2.719185726.1714990209; _gat_UA-1830249-3=1'
# PROXIES = {
#     'http': 'http://127.0.0.1:7890',
#     'https': 'https://127.0.0.1:7890'
# }
PROXIES = {}
DETAIL_DOWNLOAD_THREADS = 15
IMAGE_DOWNLOAD_THREADS = 5
USER_ID = 78789488

HEADERS = {
    "x-requested-with": "XMLHttpRequest",
    "COOKIE": COOKIE,
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
ARTISTS_BLACKLIST = ['16776564']

MAX_UPLOAD_RETRY = 10
# MAX_DOWNLOAD_RETRY = 10 