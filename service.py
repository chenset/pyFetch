# coding=utf-8
import gevent
import time
import zlib
import base64
import json
from gevent import socket


class UrlQueue():
    queue = [
        'http://www.douban.com/',
    ]

    def __init__(self):
        pass

    def get(self):
        urls = []
        for i in xrange(2):
            try:
                urls += [self.queue.pop(0)]
            except:
                pass

        print 'urls count: ', len(self.queue)
        return urls

    def add(self, urls=()):
        try:
            self.queue += urls
        except:
            pass


queue = UrlQueue()


def handle_request(data, address):
    request = json.loads(data)
    if not request or 'method' not in request:
        return json.dumps({'msg': '无法识别的请求'})

    if request['method'] == 'get':
        return json.dumps({'msg': '获取成功', 'urls': queue.get()})

    if request['method'] == 'put':
        if 'urls_add' in request:
            queue.add(request['urls_add'])

        return json.dumps({'msg': '推送成功'})

    return json.dumps({'msg': '无法识别的请求'})


def socket_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(256)
    while True:
        client, address = sock.accept()
        gevent.spawn(socket_accept, client, address)


def socket_accept(sock, address):
    try:
        buff_size = 1024
        data = sock.recv(buff_size)
        data_len = int(data[0:10])
        while len(data) < data_len:
            data += sock.recv(buff_size)

        data = zlib.decompress(base64.b64decode(data[10:]))  # 解码解压
        send_date = str(handle_request(data, address))  # 内容处理函数
        send_date = base64.b64encode(zlib.compress(send_date))  # 压缩编码
        # send content前10个字符串用于标识内容长度.
        response_len = (str(len(send_date) + 10) + ' ' * 10)[0:10]
        sock.sendall(response_len + send_date)
        sock.shutdown(socket.SHUT_WR)
    except Exception, error:
        print error
    finally:

        sock.close()


if __name__ == '__main__':
    socket_server('0.0.0.0', 7777)