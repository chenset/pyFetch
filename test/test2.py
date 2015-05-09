import time


class SS:
    d = {}


def sub(dd):
    k = 0
    while True:
        k += 1
        SS.d = dd
        print SS.d
        SS.d['w'] = k
        time.sleep(1)
