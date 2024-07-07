from . import configs, worker_
import requests
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

if __name__ == '__main__':
    processes = []
    for i in range(configs.WORKER_NUM):
        p = multiprocessing.Process(target=worker_.loop)
        p.start()
        processes.append(p)