from dogecloud import oss
from PIL import Image

storage = oss.OSS()

img = Image.open('./images/image2.jpg')
storage.upload_image_blob(img, 'image2.jpg')