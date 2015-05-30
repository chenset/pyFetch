#!coding=utf8
# import time
#
# s = time.time()
#
# for i in xrange(10000000):
# i + 1
#
# print round((time.time() - s) * 1000, 3), ' ms'


# d = {}
# d.setdefault('kk', {'fd': 1})
#
# d['kk']['gfdg'] = 23
# d.setdefault('kk', {})
# print d

#
#
# l = []
#
# l.append(0)
# l.append(1)
# l.append(2)
# l.append(3)
# l.append(4)
# l.append(5)
#
# del l[0:4]
# print l

import urllib2

# url = 'http://www.ab.com:34/'
# print (urllib2.splittype(url))
#
# print urllib2.splithost(urllib2.splittype(url)[1])


# d = {'urls': [213, 2313, 12]}
#
# print d.get('urls', [])

#
# def delete_host_freq_when_expire(expire=5):
# """
# 过滤掉根域名对应的访问时间戳列表中访问时间超出给定值的时间戳
# """
# host_freq_pool = {
# 'k': [2, 3, 4, 5, 6, 7, 8, 9],
# 'l': [1, 2, 3, 4, 5, 6, 7],
# 'a': [1, 3, 5, 4, 6, 9, 11],
# }
# now = 11
# for host, pool in host_freq_pool.items():
# for timestamp in list(pool):  # 将时间戳按从远到进排序后再循环  index 0 = 最早, index last = 最近
# if now - timestamp > expire:
# host_freq_pool[host].remove(timestamp)
# else:
# break
#
# print host_freq_pool
#
#
# delete_host_freq_when_expire()
urls = ["http://meiwen.me/src/index.html",
        "http://1000chi.com/game/index.html",
        "http://see.xidian.edu.cn/cpp/html/1429.html",
        "https://docs.python.org/2/howto/regex.html",
        """https://www.google.com.hk/search?client=aff-cs-360chromium&hs=TSj&q=url%E8%A7%A3%E6%9E%90%E5%9F%9F%E5%90%8Dre&oq=url%E8%A7%A3%E6%9E%90%E5%9F%9F%E5%90%8Dre&gs_l=serp.3...74418.86867.0.87673.28.25.2.0.0.0.541.2454.2-6j0j1j1.8.0....0...1c.1j4.53.serp..26.2.547.IuHTj4uoyHg""",
        "file:///D:/code/echarts-2.0.3/doc/example/tooltip.html",
        "http://api.mongodb.org/python/current/faq.html#is-pymongo-thread-safe",
        "https://pypi.python.org/pypi/publicsuffix/",
        "http://127.0.0.1:8000",
        "https://www.segmentfault.com.cn:802/blog/biu/1190000000330941",
        ]

import re
from urlparse import urlparse

# topHostPostfix = (
# '.com', '.la', '.io', '.co', '.info', '.net', '.org', '.me', '.mobi',
# '.us', '.biz', '.xxx', '.ca', '.co.jp', '.com.cn', '.net.cn',
# '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag', '.net.ag',
# '.org.ag', '.am', '.asia', '.at', '.be', '.com.br', '.net.br',
#     '.bz', '.com.bz', '.net.bz', '.cc', '.com.co', '.net.co',
#     '.nom.co', '.de', '.es', '.com.es', '.nom.es', '.org.es',
#     '.eu', '.fm', '.fr', '.gs', '.in', '.co.in', '.firm.in', '.gen.in',
#     '.ind.in', '.net.in', '.org.in', '.it', '.jobs', '.jp', '.ms',
#     '.com.mx', '.nl', '.nu', '.co.nz', '.net.nz', '.org.nz',
#     '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw',
#     '.hk', '.co.uk', '.me.uk', '.org.uk', '.vg', ".com.hk")
# reg = r'[^\.]+(' + '|'.join([h.replace('.', r'\.') for h in topHostPostfix]) + ')$'
# pattern = re.compile(reg, re.IGNORECASE)
# for url in urls:
#     parts = urlparse(url)
#     host = parts.netloc
#     m = pattern.search(host)
#     res = m.group() if m else host
#     # print '' if not res else res.split(':')[0]
#

def get_tld(url):
    """
    从URL中提取顶级域名
    """
    if not hasattr(get_tld, 'pattern'):
        domain_post_fix = (
            '.com', '.la', '.io', '.co', '.info', '.net', '.org', '.me', '.mobi',
            '.us', '.biz', '.xxx', '.ca', '.co.jp', '.com.cn', '.net.cn',
            '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag', '.net.ag',
            '.org.ag', '.am', '.asia', '.at', '.be', '.com.br', '.net.br',
            '.bz', '.com.bz', '.net.bz', '.cc', '.com.co', '.net.co',
            '.nom.co', '.de', '.es', '.com.es', '.nom.es', '.org.es',
            '.eu', '.fm', '.fr', '.gs', '.in', '.co.in', '.firm.in', '.gen.in',
            '.ind.in', '.net.in', '.org.in', '.it', '.jobs', '.jp', '.ms',
            '.com.mx', '.nl', '.nu', '.co.nz', '.net.nz', '.org.nz',
            '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw',
            '.hk', '.co.uk', '.me.uk', '.org.uk', '.vg', ".com.hk")
        reg = r'([^\.]+(' + '|'.join([h.replace('.', r'\.') for h in domain_post_fix]) + '))'
        get_tld.pattern = re.compile(reg, re.IGNORECASE)
        print reg

    parts = urlparse(url)
    host = parts.netloc
    """
    meiwen.me
1000chi.com
see.xidian.edu.cn
docs.python.org
www.google.com.hk

api.mongodb.org
pypi.python.org
127.0.0.1:8000
www.segmentfault.com.cn:802
"""
    m = get_tld.pattern.findall(host)
    print m
    # res = m.group() if m else host
    # return '' if not res else res.split(':')[0]


for url in urls:
    get_tld(url)