from . import configs, worker_
import requests
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from icecream import ic

if __name__ == '__main__':
    init_res = requests.get(configs.SERVER + '/crawler/image?init=true', headers=configs.HEADERS)
    ic(init_res.json())
    processes = []
    for i in range(16):
        p = multiprocessing.Process(target=worker_.loop)
        p.start()
        processes.append(p)
    for process in processes:
        process.join()