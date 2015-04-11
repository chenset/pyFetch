# coding=utf-8
import gevent
import sys
import math
import time
from gevent import socket


def client(content):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 7777))

    send_date = 's' + (str(content) * 300000) + 'e'

    # content前10个字符串用于标识内容长度.
    response_len = (str(len(send_date) + 10) + ' ' * 10)[0:10]
    sock.send(response_len + send_date)

    buff_size = 1024
    data = sock.recv(buff_size)


    # content前10个字符串用于标识内容长度.
    data_len = int(data[0:10])
    while len(data) < data_len:
        data += sock.recv(buff_size)

    print data

    sock.close()


start_time = time.time()
pool = []
for i in xrange(1000):
    pool.append(gevent.spawn(client, str(i)+'你好'))

gevent.joinall(pool)
print round((time.time() - start_time) * 1000, 2), 'ms'
