# coding=utf-8
import time
import binascii

# print '0x%x' % (binascii.crc32('ffffffff') & 0xffffffff)
#
# print int(time.time())

from mongo_single import Mongo

m = Mongo.get()

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

m.parsed.drop()
m.queue.drop()
m.result.drop()
print m.parsed.count()

# urls_data.append({'url': url, 'flag_time': 0, 'add_time': time.time(), 'slave_ip': address[0]})
#
# urls_data and Mongo.get().queue.insert(urls_data)

