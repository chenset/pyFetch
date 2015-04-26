# coding=utf-8
import gevent
import zlib
import base64
import json
from ser_handle import SerHandle
from gevent import socket
import traceback


def handle_request(data, address):
    request = json.loads(data)

    handle = SerHandle(request, address)

    if 'urls_parsed' in request and request['urls_parsed']:
        handle.urls_parsed()

    if 'urls_add' in request and request['urls_add'] and isinstance(request['urls_add'], list):
        handle.urls_add()

    if 'save' in request and request['save'] and isinstance(request['save'], list):
        handle.result_save()

        response_url_list = []
    if 'get_urls' in request:
        response_url_list = handle.get_urls()

    return json.dumps({'msg': '', 'urls': response_url_list})


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
        print traceback.format_exc()
        print error
    finally:

        sock.close()


if __name__ == '__main__':
    socket_server('0.0.0.0', 7777)