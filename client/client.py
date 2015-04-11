#-*-coding:utf-8 -*-
import time

timeStart = time.time()

import socket
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import json
import urllib2
import cookielib
import zlib
import re
import traceback
from threading import Thread
import random

socket.setdefaulttimeout(2)


class SocketKit():
    sock = None

    def __init__(self):
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        # self.sock.connect(('172.16.16.99', 9999))
        pass

    def close(self):
        # self.sock.close()
        pass

    def get_patterns(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.connect(('121.40.78.16', 9999))
        data = {
            'username': 'dsfsdfsdf',
            'password': 'fgdgd_fdsf_fdsf.gfd',
            'function': {
                'method': 'get_patterns',
            }
        }

        try:
            sock.send(json.dumps(data) + 'end[\ddd*&^@#$')
            json_string = sock.recv(1024)
            response = json.loads(json_string)
        except:
            print traceback.format_exc()
            sock.close()
            return None

        if not bool(response['success']):
            print response['msg']  # 失败处理
            sock.close()
            return None

        if not response.has_key('scan_url'):
            print '------------------------ get_patterns ----------- start -------------'
            print response
            print '------------------------ get_patterns ----------- end ---------------'
            sock.close()
            return None
        sock.close()
        return response

    def get_data(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.connect(('121.40.78.16', 9999))

        data = {
            'username': 'dsfsdfsdf',
            'password': 'fgdgd_fdsf_fdsf.gfd',
            'function': {
                'method': 'get',
            }
        }

        try:
            sock.send(json.dumps(data) + 'end[\ddd*&^@#$')
            json_string = sock.recv(1024)
            response = json.loads(json_string)
        except:
            print traceback.format_exc()
            sock.close()
            return None

        if not bool(response['success']):
            print response['msg']  # 失败处理
            return None

        if not response.has_key('url'):
            print '------------------------ get_data ----------- start -------------'
            print response
            print '------------------------ get_data ----------- end ---------------'
            sock.close()
            return None

        sock.close()
        return response['url']

    def put_data(self, parsed, urls_queue, matched=()):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.connect(('121.40.78.16', 9999))

        data = {
            'username': 'dsfsdfsdf',
            'password': 'fgdgd_fdsf_fdsf.gfd',
            'function': {
                'method': 'put',
                'urls_parsed': [],
                'urls_queue': [],
                'urls_matched': [],
            }
        }

        for url in parsed:
            data['function']['urls_parsed'].append(url)

        for url in urls_queue:
            data['function']['urls_queue'].append(url)

        for url in matched:
            data['function']['urls_matched'].append(url)

        # print data
        try:
            sock.send(json.dumps(data) + 'end[\ddd*&^@#$')
            json_string = sock.recv(1024)
            response = json.loads(json_string)
        except:
            print traceback.format_exc()
            sock.close()
            return None

        if not bool(response['success']):
            print response['msg']  # 失败处理
            sock.close()
            return None

        sock.close()
        return response


class Spider(Thread):
    url = 'http://movie.douban.com/tag/'
    host_url = ''
    kit = None
    patterns = {}
    num = 0
    failures = 0

    def __init__(self, kit):
        Thread.__init__(self)
        self.kit = kit
        self.patterns = kit.get_patterns()
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))

    def run(self):
        while True:
            time.sleep(random.randint(1, 4))

            # 连续失败10次则
            if self.failures > 10:
                self.failures = 0
                tt = 3600
                print self.getName() + ' So wrong wait %s s' % tt
                time.sleep(tt)

            if not self.get():
                self.failures += 1
                print self.getName() + ' get url failure'
                continue

            url_list = self.http_get()
            if not url_list:
                self.failures += 1
                print self.getName() + ' http failure'
                continue

            all_url_list = self.parse(url_list)
            if not all_url_list:
                print self.getName() + ' parse empty'
                continue

            filtered_list = self.filter_urls(all_url_list)
            if not filtered_list:
                self.failures += 1
                print self.getName() + ' filter failure'
                continue

            server_response = self.put(filtered_list)
            print self.url
            if server_response:
                print self.getName() + ' success'
            else:
                self.failures += 1
                print self.getName() + ' failure'
                continue

        print '---------------------------- ' + self.getName() + ' done ------------------------------------'

    def get(self):
        self.url = kit.get_data()
        if not self.url:
            return False

        self.set_host_url()  # 获取url中的协议与域名部分
        return True


    def set_host_url(self):
        protocol, rest = urllib2.splittype(self.url)
        host, rest = urllib2.splithost(rest)

        self.host_url = protocol + "://" + host

    def http_get(self):
        if self.num > 20:
            self.cookie = cookielib.CookieJar()
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
            self.num = 1

        self.num += 1
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36'
        }

        content = ''

        try:
            req = urllib2.Request(self.url, headers=headers)
            response = self.opener.open(req, timeout=10)
            print response.info()
            content = response.read()
            content = zlib.decompress(content, 16 + zlib.MAX_WBITS)
        except urllib2.HTTPError, e:
            self.failures += 1
            print 'HTTP Code: ' + str(e.code)
            return None
        except:
            self.failures += 1
            print traceback.format_exc()
            return None
        self.failures = 0
        return content
        #
        # try:
        #
        #     req = urllib2.Request(self.url, headers=headers)
        #
        #     content = urllib2.urlopen(req, timeout=10).read()  # todo 超时的异常处理 !
        #
        #     content = zlib.decompress(content, 16 + zlib.MAX_WBITS)
        # except urllib2.HTTPError, e:
        #     print 'HTTP Code: ' + str(e.code)
        #     return None
        # except:
        #     print traceback.format_exc()
        #     return None
        # return content

    def filter_urls(self, url_list):
        """
        将部分不完整的url地址转换为标准url, 再进行过滤, 转换
        """
        queue_list = []
        match_list = []
        for url, title in url_list:

            # 1.先转换url格式
            if url.startswith('.'):  # 以点开头的url
                u = self.url.rstrip('/') + "/" + url.lstrip('./')
                pass
            elif url.startswith('/'):  # 以根开头的url
                u = self.host_url.rstrip('/') + "/" + url.lstrip('/')
            else:  # 正常更是的url http开头
                u = url

            # 处理一些地址后缀有两个/的情况
            if u.endswith('/'):
                u = url.rstrip('/') + '/'

            # 将动态链接的参数部份全部去掉, 只留下静态链接部分
            u = u.split('?')[0]

            # 将链接的描点部份全部去掉, 只留下链接部分
            u = u.split('#')[0]

            # 2.通过正则过滤url ,筛选出需要添加到队列中的url
            patt = self.patterns['filter_url']  # r'^(http://movie\.douban\.com)'
            r = re.compile(patt)
            if r.search(u):
                queue_list.append((u, title.strip()))

            # 3.通过正则过滤url ,筛选出匹配命中的url
            patt = self.patterns['match_url']  # = r'^(http://movie\.douban\.com/subject/\d{5,10})'
            r = re.compile(patt)
            if r.search(u):
                match_list.append((u, title.strip()))

        return {'queue_list': queue_list, 'match_list': match_list}

    def parse(self, html):
        patt = self.patterns['scan_url']  # r'<a[^>]+href="([(\.|h|/)][^"]+)"[^>]*>([^<]+)</a>'

        r = re.compile(patt)
        match = r.findall(html)

        return match

    def put(self, result):
        queue_list = [l for l, t in result['queue_list']]
        match_list = [l for l, t in result['match_list']]
        return self.kit.put_data([self.url], queue_list, match_list)


kit = SocketKit()
spider1 = Spider(kit)
spider2 = Spider(kit)
spider3 = Spider(kit)
spider4 = Spider(kit)
# spider5 = Spider(kit)
# spider6 = Spider(kit)
# spider7 = Spider(kit)
# spider8 = Spider(kit)

spider1.start()
spider2.start()
spider3.start()
spider4.start()
# spider5.start()
# spider6.start()
# spider7.start()
# spider8.start()


'''
proxy_handler = urllib2.ProxyHandler({'': 'http://211.167.112.14:80'})
opener = urllib2.build_opener(proxy_handler)
opener.urlopen()
# urllib2.install_opener(opener)
req = urllib2.Request('http://172.16.16.153/')
print urllib2.urlopen(req, timeout=3).read()
'''

# proxy = urllib2.ProxyHandler({'http': '211.167.112.14'})
# opener = urllib2.build_opener(proxy)
# urllib2.install_opener(opener)
# print urllib2.urlopen('http://localhost:80').read()







'''
kit = SocketKit()
spider = Spider(kit)


spider.get()
url_list = spider.http_get()
server_respone = spider.put(spider.filter_urls(spider.parse(url_list)))
print spider.url
if server_respone:
    print server_respone
else:
    print 'failure'
'''

'''
urls = [r'<a href="http://www.miibeian.gov.cn/">gdfgdfg</a>',
        r'313<a href="http://www.douban.com/location/shenzhen/events">同城活动</a>4234',
        r'<a target="_blank" class="lnk-movie" href="http://movie.douban.com">豆瓣电影</a>',
        'http://movie.douban.com/gsgsd/gsd/fg', 'gffffhhgdhrefsdf', 'http://movie.douban.com/subject/2063914/',
        'http://movie.douban.com/subject/10440138/?from=subject-page']

# patt = r'^(http://movie\.douban\.com)'
patt = r'^(http://movie\.douban\.com/subject/\d{5,10})'

r = re.compile(patt)

for url in urls:
    match = r.search(url)

    print match


import MySQLdb

conn = MySQLdb.connect(host="172.16.16.99", user="root", passwd="chen", db="spider", charset="utf8")

cursor = conn.cursor()

sql = "select * from url_pool"

cursor.execute(sql)

pattern = r'^(http://movie\.douban\.com/subject/\d{5,10}/(\?|$))'
pattern = r'^(http://movie\.douban\.com/subject/\d{5,10}/(\?|$))'
r = re.compile(pattern)
i = 0
j = 0
for row in cursor.fetchall():
    url = row[1]
    # if url.endswith('/'):
    #     url = url.rstrip('/') + '/'

    if not r.search(str(url)):
        i += 1
        print row[1]
    else:
        j += 1

print 'not ' + str(i)
print 'yes ' + str(j)

s = 'sdfsdf//'

print s.strip('/')
'''

print str(round((time.time() - timeStart) * 1000, 3)) + 'ms'







