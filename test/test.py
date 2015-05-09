#! coding=utf-8
from multiprocessing import Process, Manager, Queue
import time
from test2 import sub


if __name__ == '__main__':
    d = Manager().dict()
    p = Process(target=sub, args=(d,))
    p.start()
    d['wff11'] = '23132'
    p.join()
    # k = 1000
    # while True:
    # k += 1
    #     print d
    #     d['wff'] = k
    #     time.sleep(1)