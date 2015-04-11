# coding=utf-8
import time

start_time = time.time()
for i in xrange(100000):
    len('2222' * i)

print round((time.time() - start_time) * 1000, 2), 'ms'