from hashlib import sha1
import hmac
import boto3.session
import requests
import json
import urllib
from io import BytesIO

import boto3

from icecream import ic
from cache import cache
from . import keys

from PIL import Image


def dogecloud_api(api_path, data={}, json_mode=False):
    """
    调用多吉云API

    :param api_path:    调用的 API 接口地址，包含 URL 请求参数 QueryString，例如：/console/vfetch/add.json?url=xxx&a=1&b=2
    :param data:        POST 的数据，字典，例如 {'a': 1, 'b': 2}，传递此参数表示不是 GET 请求而是 POST 请求
    :param json_mode:   数据 data 是否以 JSON 格式请求，默认为 false 则使用表单形式（a=1&b=2）

    :type api_path: string
    :type data: dict
    :type json_mode bool

    :return dict: 返回的数据
    """

    # 这里替换为你的多吉云永久 AccessKey 和 SecretKey，可在用户中心 - 密钥管理中查看
    # 请勿在客户端暴露 AccessKey 和 SecretKey，否则恶意用户将获得账号完全控制权
    access_key = keys.ACCESS_KEY
    secret_key = keys.SECRET_KEY

    body = ''
    mime = ''
    if json_mode:
        body = json.dumps(data)
        mime = 'application/json'
    else:
        body = urllib.parse.urlencode(data)  # Python 2 可以直接用 urllib.urlencode
        mime = 'application/x-www-form-urlencoded'
    sign_str = api_path + "\n" + body
    signed_data = hmac.new(secret_key.encode('utf-8'),
                           sign_str.encode('utf-8'), sha1)
    sign = signed_data.digest().hex()
    authorization = 'TOKEN ' + access_key + ':' + sign
    response = requests.post('https://api.dogecloud.com' + api_path,
                             data=body,
                             headers={
                                 'Authorization': authorization,
                                 'Content-Type': mime
                             })
    return response.json()


EXPIRE_TIME = 2 * 60 * 60
DEBUG = False


def get_tmp_token():
    """
    获取临时密钥
    """

    if cache.get('accessKeyId') and cache.get('accessKeySecret'):
        return

    res = dogecloud_api('/auth/tmp_token.json', {
        'channel': 'OSS_FULL',
        'scopes': ['*']
    }, True)

    if res['code'] != 200:
        print("api failed: " + res['msg'])  # 失败
        quit()

    credentials = res['data']['Credentials']
    s3Bucket = res['data']['Buckets'][0]['s3Bucket'],
    s3Endpoint = res['data']['Buckets'][0]['s3Endpoint']

    cache.set('accessKeyId', credentials['accessKeyId'], EXPIRE_TIME)
    cache.set('secretAccessKey', credentials['secretAccessKey'], EXPIRE_TIME)
    cache.set('sessionToken', credentials['sessionToken'], EXPIRE_TIME)
    cache.set('s3Bucket', s3Bucket[0], EXPIRE_TIME)
    cache.set('s3Endpoint', s3Endpoint, EXPIRE_TIME)


class OSS:

    def __init__(self):

        get_tmp_token()
        self.bucket = cache.get('s3Bucket')

        self.s3 = boto3.client(
            's3',
            aws_access_key_id=cache.get('accessKeyId'),
            aws_secret_access_key=cache.get('secretAccessKey'),
            aws_session_token=cache.get('sessionToken'),
            endpoint_url='https://' + self.bucket + '.' +
            cache.get('s3Endpoint').replace('https://', ''))

    def upload_image_file(self, image_path: str, image_uri: str):
        """
        上传图片到 OSS
        """
        get_tmp_token()
        bucket = self.bucket
        key = image_uri
        self.s3.upload_file(image_path, bucket, key)
        return image_uri

    def upload_image_blob(self, image_blob: Image, image_uri: str):
        get_tmp_token()
        image_file = self.image_blob_to_file_obj(image_blob)
        bucket = self.bucket
        key = image_uri
        self.s3.upload_fileobj(image_file, bucket, key)
        return image_uri

    def delete_file(self, image_uri: str):
        """删除 OSS 中的指定文件，不影响本地文件。"""
        get_tmp_token()
        bucket = self.bucket
        key = image_uri
        return self.s3.delete_object(Bucket=bucket, Key=key)

    def image_blob_to_file_obj(self, image_blob: Image):
        img_byte_arr = BytesIO()

        # 将图像保存到 BytesIO 对象中，格式为 JPEG
        image_blob.save(img_byte_arr, format='JPEG')

        # 使用 BytesIO 对象的内容创建一个 File 对象
        img_byte_arr.seek(0)  # 将光标移到文件的开头
        img_file = img_byte_arr
        return img_file

    def get_file_list(self, continue_file='', prefix='', limit=200):
        data = []
        params = {
            'prefix': cache.get('s3Bucket') + '/' + prefix,
        }
        url = f"/oss/file/list.json?bucket=randimg&prefix={params['prefix']}&continue={continue_file}&limit={limit}"
        sign_str = url + ("\n" + "")

        signedData = hmac.new(keys.SECRET_KEY.encode(),
                              sign_str.encode('utf-8'), sha1)
        token = signedData.digest().hex()
        headers = {
            "Host": 'api.dogecloud.com',
            'Authorization': f'TOKEN {keys.ACCESS_KEY}:{token}'
        }
        res = requests.get("https://api.dogecloud.com" + url, headers=headers)

        if res.status_code == 200:
            json_data = res.json()
            if json_data['code'] == 200:
                con = json_data['data'].get('continue')
                data = json_data['data']['files']
            if con != None:
                data += self.get_file_list(con, prefix, limit)
            return data
