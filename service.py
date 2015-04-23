# coding=utf-8
import gevent
import time
import zlib
import base64
import json
from gevent import socket


class DB():
    data = []

    def __init__(self):
        pass

    def add(self, data=()):
        try:
            self.data += data
        except:
            pass

        print 'DB data: ', self.data


class UrlQueue():
    queue_urls = [
        'http://www.douban.com/',
    ]

    queue_parsed = []

    def __init__(self):
        pass

    def get(self):
        urls = []
        for i in xrange(2):
            try:
                urls += [self.queue_urls.pop(0)]
            except:
                pass

        print 'urls count: ', len(self.queue_urls)
        print 'urls parsed count: ', len(self.queue_parsed)
        return urls

    def add_parsed(self, urls=()):
        try:
            self.queue_parsed += urls
        except:
            pass

    def add(self, urls=()):
        try:
            self.queue_urls += urls
        except:
            pass


queue = UrlQueue()
db = DB()


def handle_request(data, address):
    request = json.loads(data)
    if not request or 'method' not in request:
        return json.dumps({'msg': '无法识别的请求'})

    if request['method'] == 'get':
        return json.dumps({'msg': '获取成功', 'urls': queue.get()})

    if request['method'] == 'put':
        if 'urls_parsed' in request and request['urls_parsed']:
            queue.add_parsed(request['urls_parsed'])

        if 'urls_add' in request and request['urls_add']:
            queue.add(request['urls_add'])

        if 'save' in request and request['save']:
            db.add(request['save'])

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