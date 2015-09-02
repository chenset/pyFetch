# coding=utf-8
from mongo_single import Mongo
from bson import ObjectId
import requests
import urllib2
from requests import Request, Session
from contextlib import closing
import time
from tld import get_tld
import re
# print Mongo.get()['temp_doc_'].insert_one({'df': '123', 'gfg': '1234'})
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

start_time = time.time()

# d = {'a': {'b': 1}}
#
# del d['a']['b']
#
# print d

ll = {'b': 1,
      'a': [{u'domain': u'jandan.net', u'add_time': 1441030872}, {u'domain': u'jandan.net', u'add_time': 1441030873},
            {u'domain': u'jandan.net', u'add_time': 1441030874}, {u'domain': u'jandan.net', u'add_time': 1441030875},
            {u'domain': u'jandan.net', u'add_time': 1441030878}, {u'domain': u'jandan.net', u'add_time': 1441030879},
            {'domain': u'jandan.net', 'add_time': 1441030887}, {'domain': u'jandan.net', 'add_time': 1441030888}]
      }

tt = ll['a'][:]
# for i in tt:
#     ll['a'].remove(i)

print ll

# print ll['a']



# j = 0
# for i in range(100000000):
# j += i
#
# print j
# print int("http://bbs.qq.com/finance/1120202.html")
#
# base_url = "".join("http://bbs.qq.com/finance/1120202.html")  # 删除所有\s+
# protocol, rest = urllib2.splittype(base_url)
# host, rest = urllib2.splithost(rest)
# print host
#
# print get_tld("http://bbs.qq.com/finance/1120202.html")
#
# #
# res = requests.session().get('http://xiazai.xiazaiba.com/Android/I/com.iooly.android.lockscreen_480200_XiaZaiBa.apk',
# stream=True)
# print requests.session().get('http://www.qq.com/?gdg    dg=df g').content
# import requests
# from contextlib import closing
#
#
# def format_and_filter_urls(base_url, url):
# # 转换非完整的url格式
# if url.startswith('/'):  # 以根开头的绝对url地址
# base_url = "".join(base_url.split())
# protocol, rest = urllib2.splittype(base_url)
# host, rest = urllib2.splithost(rest)
# print '--------------------------------------'
# print base_url
# print url
# print protocol
#         print rest
#         print host
#         print '======================================'
#         url = (protocol + "://" + host).rstrip('/') + "/" + url.lstrip('/')
#
#     if url.startswith('.') or not url.startswith('http'):  # 相对url地址
#         url = base_url.rstrip('/') + "/" + url.lstrip('./')
#
#     # 过滤描点
#     return url.split('#')[0]
#
#
# b = "http://news.sogou.c       om/news?ie=utf8&p=40230447&interV=kKIOkrELjbgPmLkEmrELjbkRmLkElbYTkKIKmbELjboJmLkElbkTkKIOkrELjbgPmLkEmrELjbkR\r\n\
# mLkElbYTkKIKmbELjboJmLkElbk=_-1328353157&query=%27%20%20%20encodeURIComponent%28arr%5Bi%5D%29%20%20%20%27"
#
# u = '/image.shtml?type=1&rank=0'
#
# print format_and_filter_urls(b, u)
# size_limit = 1000000000
# content = ''
# with closing(
# requests.get('mLkElbYTkKIKmbELjboJmLkElbk=_-1328353157&query=%27%20%20%20encodeURIComponent%28arr%5Bi%5D%29%20%20%20%27',
# stream=True)) as req:
#
# if not req.encoding == 'utf-8':
#         req.encoding = 'utf-8'
#
#     if 'content-length' in req.headers:
#         if int(req.headers['content-length']) > size_limit:
#             raise Exception(
#                 'content-length too many. content-length: ' + str(req.headers['content-length']))
#
#         content = req.content
#
#     else:
#         size_temp = 0
#         for line in req.iter_lines():
#             if line:
#                 size_temp += len(line)
#                 if size_temp > size_limit:
#                     raise Exception('content-length too many.')
#
#                 content += line
#
# print content

#
# res = requests.get('http://www.xiazaiba.com/', timeout=10)
# if not res.encoding == 'utf-8':
#     res.encoding = 'utf-8'
# content = res.content
#
# title_patt = r'<title[^>]*>([^<]*)</title>'
# title_r = re.compile(title_patt)
# title_match = title_r.findall(content)
# title = ''
# if title_match:
#     title = title_match[0]
#
#
# print title
# print len(res.content)
#
# for line in r.iter_lines():
#
# # filter out keep-alive new lines
# if line:
# print(json.loads(line))
# res = requests.Session().get('http://github.com', allow_redirects=True)
#
# s = Session()
# req = Request('GET', 'http://xiazai.xiazaiba.com/Android/I/com.iooly.android.lockscreen_480200_XiaZaiBa.apk', )
# prepped = req.prepare()


# print prepped.url
# print prepped.status_code
# print prepped.headers
# do something with prepped.body
# do something with prepped.headers

# resp = s.send(prepped,
# stream=stream,
# verify=verify,
# proxies=proxies,
# cert=cert,
# timeout=timeout
# )

# print(resp.status_code)

print round((time.time() - start_time) * 1000, 2), ' ms'