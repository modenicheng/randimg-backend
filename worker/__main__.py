from . import configs, worker_, utils
import requests
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from icecream import ic
import time
import numpy as np
if __name__ == '__main__':
    # init_res = requests.get(configs.SERVER + '/crawler/image?init=true', headers=configs.HEADERS)
    # if init_res.status_code != 200:
    #     print(f"init response status {init_res.status_code}, now exit...")
    #     exit()
    # ic(init_res.json())
    # processes = []
    # for i in range(16):
    #     p = multiprocessing.Process(target=worker_.loop)
    #     p.start()
    #     processes.append(p)
    # for process in processes:
    #     process.join()
    # # t = time.time()
    # # utils.get_dominant_colors('images\image.jpg')
    # # ic(time.time() - t)
    
    # utils.is_blank_background("images\\105366418_p0.jpg")
    # utils.is_blank_background("images\\108979248_p0.jpg")
    # utils.is_blank_background("images\\119481189_p0.jpg")
    # utils.is_blank_background("images\\108979248_p0.jpg")
    while True:
        i = input(">>>")
        if 'http' in i:
            print('Fetch:', i)
            res = requests.get(i, stream=True)
            i = np.asarray(bytearray(res.content), dtype="uint8")
        t = time.time()
        try:
            ic(utils.is_blank_background(i))
        except Exception as e:
            print(e)
        ic(time.time() - t)
    
    # init_res = requests.get(configs.SERVER + '/adjust-accessible?init=true', headers=configs.HEADERS)
    # if init_res.status_code != 200:
    #     print(f"init response status {init_res.status_code}, now exit...")
    #     exit()
    # ic(init_res.json())
    # processes = []
    # for i in range(configs.WORKER_NUM * 2):
    #     p = multiprocessing.Process(target=worker_.loop_2)
    #     p.start()
    #     processes.append(p)
    # for process in processes:
    #     process.join()