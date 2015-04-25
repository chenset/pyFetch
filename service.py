# coding=utf-8
import gevent
import time
import zlib
import base64
import json
from gevent import socket
from mongo_single import Mongo


def handle_request(data, address):
    request = json.loads(data)

    response_url_list = []
    if 'get_urls' in request:
        ids = []
        for doc in Mongo.get().queue.find({'flag_time': {'$lt': int(time.time() - 300)}}).limit(
                10):  # 取标识时间早于当前时间300秒之前的url
            ids.append(doc['_id'])
            response_url_list.append(doc['url'])

        # todo 多线程情况下, 这里线程非安全
        ids and Mongo.get().queue.update({'_id': {'$in': ids}}, {'$set': {'flag_time': int(time.time())}},
                                         multi=True)

        # todo 没有地址的情况下给一个  test !!
        if not response_url_list:
            response_url_list.append('http://www.douban.com/')

    if 'urls_parsed' in request and request['urls_parsed']:
        urls_data = []
        url_list = []
        for url in request['urls_parsed']:
            url_list.append(url)
            urls_data.append({'url': url, 'add_time': int(time.time()), 'slave_ip': address[0]})

        Mongo.get().queue.remove({'url': {'$in': url_list}}, multi=True)  # 删除抓取完毕的队列

        urls_data and Mongo.get().parsed.insert(urls_data)

    if 'urls_add' in request and request['urls_add']:
        url_list = []
        for url in request['urls_add']:
            url_list.append(url)

        url_list = list(set(url_list))

        exist_url_list = []
        for doc in Mongo.get().queue.find({'url': {'$in': url_list}}):
            exist_url_list.append(doc['url'])

        urls_data = []
        for url in url_list:
            if url not in exist_url_list:
                urls_data.append({'url': url, 'flag_time': 0, 'add_time': int(time.time()), 'slave_ip': address[0]})

        urls_data and Mongo.get().queue.insert(urls_data)

    if 'save' in request and request['save'] and isinstance(request['save'], dict):
        Mongo.get().result.insert(request['save'])

    return json.dumps({'msg': '获取成功', 'urls': response_url_list})


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