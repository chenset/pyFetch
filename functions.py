#! coding=utf-8
import hashlib
import sys
import time
import urllib2
import re
from mongo_single import Mongo


def get_project_list():
    """
    todo 测试是否支持中文
    :return:
    """
    get_project_list.cache = [v for v in Mongo.get().projects.find({}, {'_id': 0})]

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
        urls.append(format_and_filter_urls(base_url, url))

    return urls
