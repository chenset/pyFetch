# coding=utf-8
import gevent
import time
import math
from gevent import socket


def server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', port))
    sock.listen(256)
    while True:
        cli, addr = sock.accept()
        gevent.spawn(handle_request, cli)


def handle_request(s):
    try:
        buff_size = 1024
        data = s.recv(buff_size)
        for i in xrange(int(math.ceil(float(data[0:10]) / buff_size)) - 1):
            data += s.recv(buff_size)

        send_date = str(data)
        print send_date

        # send content前10个字符串用于标识内容长度.
        response_len = (str(len(send_date) + 10) + ' ' * 10)[0:10]
        s.send(response_len + send_date)
        s.shutdown(socket.SHUT_WR)
    except Exception, ex:
        print ex
    finally:

        s.close()


if __name__ == '__main__':
    server(7777)