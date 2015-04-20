# coding=utf-8
# import gevent
# import sys
# import time
import zlib
import base64
import socket
# from gevent import socket


def socket_client(content):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect(('10.0.0.10', 7777))
    sock.connect(('127.0.0.1', 7777))

    send_date = base64.b64encode(zlib.compress(content))  # 压缩编码

    # content前10个字符串用于标识内容长度.
    response_len = (str(len(send_date) + 10) + ' ' * 10)[0:10]
    sock.sendall(response_len + send_date)
    buff_size = 1024
    data = sock.recv(buff_size)

    # content前10个字符串用于标识内容长度.
    data_len = int(data[0:10])
    while len(data) < data_len:
        s = sock.recv(buff_size)
        data += s

    data = zlib.decompress(base64.b64decode(data[10:]))  # 解码解压

    sock.close()

    return data

#
# start_time = time.time()
# pool = []
# for i in xrange(2):
#     pool.append(gevent.spawn(socket_client, str(i) + '你好'))
#
# gevent.joinall(pool)
#
# print round((time.time() - start_time) * 1000, 2), 'ms'
