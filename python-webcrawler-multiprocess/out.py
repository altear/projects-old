import multiprocessing as mp
import logging
import sys
import time

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

def worker(queue):
    logger.info('hi')
    queue.put(1)
    return 

if __name__ == '__main__':
    logger.info('hey')
    
    with mp.Pool(4) as pool, mp.Manager() as m:
        queue = m.Queue()
        pool.apply_async(worker, (queue,))
        pool.apply_async(worker, (queue,))
        pool.close()
        pool.join()
        print(queue.get(False, 1))