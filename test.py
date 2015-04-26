# coding=utf-8
import time
import binascii

# print '0x%x' % (binascii.crc32('ffffffff') & 0xffffffff)
#
# print int(time.time())

from mongo_single import Mongo

m = Mongo.get()
start_time = time.time()

# for i in xrange(100):
# m.parsed.insert([{'url': '1'}, {'url': '11'}])

# print m.parsed.find_and_modify(query={'url': '1'}, remove=True)

# for url in m.parsed.find_and_modify(query={'url': 'sfsdfsdfsf'}, remove=True):
# print url
#
# ids = []
# for doc in m.parsed.find().limit(1200):
# print doc
# ids.append(doc['_id'])
#
# m.parsed.remove({'_id': {'$in': ids}}, multi=True)
#
m.parsed.drop()
m.queue.drop()
m.result.drop()
print m.parsed.count()

# print m.parsed.ensure_index('url', unique=True)
# print m.queue.ensure_index('url', unique=True)
import hashlib





import zlib


# for i in xrange(1000000):
# # binascii.crc32('pojqhnulnxu' + str(i))
# md5('pojqhnulnxu' + str(i))

# print binascii.crc32('htpqwklvynl')

# print md5('pojqhnulnxu')


# print 2**32
#
# m.test.drop()
# # m.test.insert([{'t': i} for i in xrange(10000)])
#
# # print m.test.count()
# import requests
# requests.get('hot?p=2')
# try:
# requests.get('hot?p=2')
# except requests.URLRequired:
# print 1

# RequestException, Timeout, URLRequired,
# TooManyRedirects, HTTPError, ConnectionError

# urls_data.append({'url': url, 'flag_time': 0, 'add_time': time.time(), 'slave_ip': address[0]})
#
# urls_data and Mongo.get().queue.insert(urls_data)
class A():
    attr = 1


A.attr = 2
print A.attr

a = A()
a.attr = 3
print a.attr

print A.attr
A.attr = 4

print a.attr

print round((time.time() - start_time) * 1000, 2)