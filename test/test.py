#!coding=utf8
import time

s = time.time()

for i in xrange(10000000):
    i + 1

print round((time.time() - s) * 1000, 3), ' ms'