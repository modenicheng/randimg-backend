import threading
from dogecloud import oss
from db import crud


def upload_image_file(image_file_path: str, key: str):
    storage=oss.OSS()
    upload_image(image_file_path, key, storage)
    del storage
    
def upload_image(image_file_path: str, key: str, storage: oss.OSS):
    if crud.is_image_uploaded(key): 
        print(
        f'| {threading.current_thread().name} | {key} is uploaded. Skip'
    )
        return
    storage.upload_image_file(image_file_path, key)
    crud.uploaded_image(key)
    print(
        f'| {threading.current_thread().name} | ==>> Uploaded {image_file_path} to {key}'
    )