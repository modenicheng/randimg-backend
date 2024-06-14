from dogecloud import oss
from cache import cache
storage = oss.OSS()

storage.upload('./images/image.jpg', 'image.jpg')
# oss.get_tmp_token()