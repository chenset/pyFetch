#encoding=utf-8
from mysql_single import Mysql
from bloomfilter_single import BL
from bloomfilter_matched_single import BLMatched
from redis_single import Redis
import random


def random_info():
    """
     爬虫统计写入文件, 随机触发, 目前概率 1/100
    """
    if 1 == int(random.random() * 100):
        with open('/tmp/queue.txt', 'w') as f:
            f.write(str('\r\n'.join(info())))


def info():
    log = []
    r = Redis.get()
    log.append('r: ' + str(r.llen('url')))

    bl = BL.get()
    log.append('bl: ' + str(len(bl)))

    bl_match = BLMatched.get()
    log.append('bl_match: ' + str(len(bl_match)))

    conn = Mysql.get()
    cursor = conn.cursor()
    cursor.execute("select count(*) from url_pool")
    for row in cursor.fetchall():
        log.append('url_pool: ' + str(row[0]))

    cursor.execute("select count(*) from url_parsed")
    for row in cursor.fetchall():
        log.append('url_parsed: ' + str(row[0]))
    cursor.close()
    return log


def clear():
    r = Redis.get()
    r.delete('url')

    bl_match = BLMatched.get()
    bl_match.update(())

    bl = BL.get()
    bl.update(())

    conn = Mysql.get()
    cursor = conn.cursor()
    sql = "truncate table url_pool;"
    cursor.execute(sql)
    sql = "truncate table url_parsed;"
    cursor.execute(sql)
    cursor.close()
    print 'clear done'


def queue_save():
    """
    队列操作, 将内存中的数据保存到硬盘中, 持久化
    """
    r = Redis.get()
    r.save()


def get_patterns():
    """
    返回客户机需要的正则表达式模式
    """
    # www.movie.douban.com
    return {
        'msg': 'Here you are',
        'success': True,
        'scan_url': r'<a[^>]+href="([(\.|h|/)][^"]+)"[^>]*>([^<]+)</a>',
        'filter_url': r'^(http://movie\.douban\.com)',
        'match_url': r'^(http://movie\.douban\.com/subject/\d{5,10}/(\?|$))'
    }

    # www.ifanr.com
    return {
        'msg': 'Here you are',
        'success': True,
        'scan_url': r'<a[^>]+href="([(\.|h|/)][^"]+)"[^>]*>([^<]+)</a>',
        'filter_url': r'^(http://www\.ifanr\.com)',
        'match_url': r'^(http://www\.ifanr\.com/\d{5,10}(/|$))'
    }


def get():
    """
    返回一个队列给客户端
    """
    r = Redis.get()
    url = r.lpop('url')

    if url is None:
        return {'msg': 'queues is empty', 'success': False}
    else:
        return {'msg': 'execute done', 'success': True, 'url': url}


def init():
    """
    用于程序初始化的时候
    """

    conn = Mysql.get()
    cur = conn.cursor()

    sql = "select url from url_pool"
    cur.execute(sql)
    bl_match = BLMatched.get()
    for row in cur.fetchall():
        bl_match.add(row[0])

    r = Redis.get()
    bl = BL.get()
    bl.update(r.lrange('url', 0, -1))


def put(data):
    """
    处理客户端发过来的数据
    """

    #保存已经解析过的
    if data.has_key('urls_parsed'):
        for url in data['urls_parsed']:
            insert_parsed(url)

    #保存解析过且匹配的
    if data.has_key('urls_matched'):
        for url in data['urls_matched']:

            bl_match = BLMatched.get()
            if url not in bl_match:  # url判重, 只往url_pool中加入未曾加入过的url.
                bl_match.add(url)
                insert_matched(url)

    #将新url入队列
    if data.has_key('urls_queue'):
        r = Redis.get()
        bl = BL.get()

        for url in data['urls_queue']:
            if url not in bl:  # url判重, 只往队列中加入未曾加入过的url
                bl.add(url)
                r.lpush('url', url)

    return {'msg': 'execute done', 'success': True}


def bf_update():
    """
    BL批量更新, 一般用于程序初始化的时候
    """
    # todo 注意这里, 很容易超出内存大小
    # r = Redis.get()
    # r.get('url')

    # bl = BL.get()
    # bl.update(var)

    pass


def insert_parsed(url, close=False):
    """
    将已经解析过的url存入数据库表url_parsed
    """
    conn = Mysql.get()
    cursor = conn.cursor()
    sql = "insert into url_parsed(url,encode_url,status,add_time) values(%s,crc32(%s),%s,unix_timestamp())"
    param = (url, url, 1)
    n = cursor.execute(sql, param)
    if close:
        cursor.close()
    if n < 1:
        return False

    return True


def insert_matched(url, close=False):
    """
    将匹配的url放入数据库表url_pool
    """
    conn = Mysql.get()
    cursor = conn.cursor()
    sql = "insert into url_pool(url,encode_url,status,add_time) values(%s,crc32(%s),%s,unix_timestamp())"
    param = (url, url, 1)
    n = cursor.execute(sql, param)
    if close:
        cursor.close()
    if n < 1:
        return False

    return True
