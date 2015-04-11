#!/usr/bin/python
#encoding=utf-8
import time
import fun
import sys

start_time = time.time()

print '\r\n'
from socket_server import SocketServer
from redis_single import Redis

# fun.clear()
fun.init()

# print fun.put({'urls_queue': ['http://movie.douban.com/new_subject?cat=1002&amp;search_text=山崎静代']})
# print fun.put({'urls_queue': ['http://movie.douban.com']})
# print fun.put({'urls_queue': ['http://movie.douban.com/tag/']})
# print fun.put({'urls_queue': ['http://movie.douban.com/trailers']})
# fun.put({'urls_queue': ['http://www.ifanr.com/426862']})
# r.delete('')
# print r.llen('url')
# for i in xrange(10000):
#     r.lpush('url', i**2)
#     pass
#

# print r.lpop(name='url')

# print r.llen('url')
# print r.dbsize()

# r.save()
# r.shutdown()


sock = SocketServer()
sock.listen()


# fun.bf_add('fsdf')

# print fun.bf_in('fsdf')



print '\r\n' + str((time.time() - start_time) * 1000) + 'ms'

'''
import time


def insert_url(url, close=False):
    cursor = Mysql.get()
    sql = "insert into url_pool(url,encode_url,status) values(%s,crc32(%s),%s)"
    param = (url, url, 1)
    n = cursor.execute(sql, param)
    if close:
        cursor.close()

    return n

#连接
conn=MySQLdb.connect(host="localhost",user="root",passwd="",db="test",charset="utf8")
cursor = conn.cursor()

#写入
sql = "insert into user(name,created) values(%s,%s)"
param = ("aaa",int(time.time()))
n = cursor.execute(sql,param)
print n

#更新
sql = "update user set name=%s where id=3"
param = ("bbb")
n = cursor.execute(sql,param)
print n

#查询
n = cursor.execute("select * from user")
for row in cursor.fetchall():
    for r in row:
        print r

#删除
sql = "delete from user where name=%s"
param =("aaa")
n = cursor.execute(sql,param)
print n
cursor.close()

#关闭
conn.close()

'''