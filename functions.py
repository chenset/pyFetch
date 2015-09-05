# coding=utf-8
import hashlib
import time
import urllib2
import re
import sys
import StringIO
import contextlib
from tld import get_tld
from mongo_single import Mongo
import requests


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


def mix_ip(ip):
    ip_fragment = ip.split('.')
    ip_fragment[1] = ip_fragment[1].zfill(3)
    ip_fragment[2] = ip_fragment[2].zfill(3)
    ip_fragment[1] = ip_fragment[1][0:2] + '*'
    # ip_fragment[2] = '**' + ip_fragment[2][2:]
    ip_fragment[2] = '***'
    return '.'.join(ip_fragment)


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


def smarty_encode(text):
    chars = text[0: 1000].lower()
    if chars.find('charset=utf-8') != -1 and chars.find('chiphell') != -1:  # 一些编码不标准的站点的特殊处理
        return text

    for k in ['utf-8', 'gb18030', 'ISO-8859-2', 'ISO-8859-1', 'gb2312', 'gbk']:
        try:
            return unicode(text, k)
        except:
            continue

    raise Exception('Had no way to encode')


def get_domain(url):
    try:
        return get_tld(url)
    except:
        base_url = "".join(url)  # 删除所有\s+
        protocol, rest = urllib2.splittype(base_url)
        host, rest = urllib2.splithost(rest)
        return host


def fetch_ip(content):
    result = re.search(
        '((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))',
        content)
    if not result:
        return None
    return result.group(0)


def get_wan_ip():
    server_list = (
        # 获取wan ip的网站地址, 可以自己添加更多
        'http://wanip.sinaapp.com/',
        'http://1111.ip138.com/ic.asp',
        'http://city.ip138.com/ip2city.asp',
        'http://www.ip38.com/',
    )

    for url in server_list:
        try:
            html = requests.get(url)
            ip = fetch_ip(html.content)

        except:
            continue
        else:
            return ip

