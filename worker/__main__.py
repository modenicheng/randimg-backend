from . import configs, worker_
import requests
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

if __name__ == '__main__':
    # res = requests.get(configs.SERVER + 'crawler/image-list')
    # l = res.json()
    processes = []
    for i in range(configs.WORKER_NUM):
        p = multiprocessing.Process(target=worker_.worker)
        p.start()
        processes.append(p)