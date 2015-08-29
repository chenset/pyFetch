# coding=utf-8
import hashlib
import time
import urllib2
import re
import sys
import StringIO
import contextlib
import zlib
import base64
# from gevent import socket
import socket

from mongo_single import Mongo


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def get_project_list():
    """
    todo 测试是否支持中文
    :return:
    """
    # get_project_list.cache = [v for v in Mongo.get().projects.find({}, {'_id': 0})]
    get_project_list.cache = [v for v in Mongo.get().projects.find()]

    return get_project_list.cache


def md5(s):
    __md5 = hashlib.md5()
    __md5.update(str(s))
    return __md5.hexdigest()


def echo_err(msg):
    sys.stderr.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' ' + msg + '\r\n')


def format_and_filter_urls(base_url, url):
    # 转换非完整的url格式
    if url.startswith('/'):  # 以根开头的绝对url地址
        base_url = "".join(base_url.split())  # 删除所有\s+
        protocol, rest = urllib2.splittype(base_url)
        host, rest = urllib2.splithost(rest)
        url = (protocol + "://" + host).rstrip('/') + "/" + url.lstrip('/')

    if url.startswith('.') or not url.startswith('http'):  # 相对url地址
        url = base_url.rstrip('/') + "/" + url.lstrip('./')

    # 过滤描点
    return url.split('#')[0]


def get_urls_form_html(base_url, html):
    patt = r'<a[^>]+href="([(\.|h|/)][^"]+)"[^>]*>[^<]+</a>'
    r = re.compile(patt)
    match = r.findall(html)
    urls = []
    for url in match:
        url and urls.append(format_and_filter_urls(base_url, url))

    return urls


def socket_client(content):
    """
    Slave与Master的socket通讯client端
    使用特定格式传输
    传输时会压缩数据
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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


def smarty_encode(text):
    for k in ['utf-8', 'gb18030', 'ISO-8859-2', 'ISO-8859-1', 'gb2312', 'gbk']:
        try:
            return unicode(text, k)
        except:
            continue

    raise Exception('Had no way to encode')
