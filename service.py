# coding=utf-8
import gevent
import time
import zlib
import base64
import json
from gevent import socket


def handle_request(data, address):
    request = json.loads(data)
    if not request or 'method' not in request:
        return json.dumps({'msg': '无法识别的请求'})

    if request['method'] == 'get':
        return json.dumps({'msg': '获取成功', 'urls': [
            'http://www.douban.com/',
            'http://movie.douban.com/subject/23761370/',
            'http://movie.douban.com/subject/23761360/',
            'http://movie.douban.com/subject/23761350/',
            'http://movie.douban.com/subject/23761340/',
            'http://movie.douban.com/subject/23761330/',
            'http://movie.douban.com/subject/23761320/',
            'http://movie.douban.com/subject/23761310/',
            'http://movie.douban.com/subject/23761380/',
            'http://movie.douban.com/subject/23761390/',
        ]})

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