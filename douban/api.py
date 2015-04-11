#!/usr/bin/python
# -*- coding:utf-8 -*-

import time

start_time = time.time()
import re
import sys
import cookielib
import urllib2
import zlib
import traceback
import thread
import json
import logging

LOG_FILENAME = '/tmp/logging.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, )

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('..')
import MySQLdb


class Mysql:
    instance = None
    conn = None
    cursor = None

    def __init__(self):
        self.conn = MySQLdb.connect(host="121.40.78.16", user="spider", passwd="0xjdlakosh", db="spider",
                                    charset="utf8")

    @staticmethod
    def get():
        mysql = Mysql.get_instance()
        return mysql.conn

    @staticmethod
    def get_instance():
        if Mysql.instance is None:
            Mysql.instance = Mysql()

        return Mysql.instance


conn = Mysql.get()
cur = conn.cursor()
cur.execute("truncate table movie;"
            " truncate table genre;"
            " truncate table countrie;"
            " truncate table movie_director_map; "
            "truncate table director;"
            " truncate table movie_cast_map;"
            " truncate table cast;")
cur.close()
cur = conn.cursor()

start_point = 0
increase = 40  # 并发数量
sleep_s = 60  # 睡眠秒数
sql_arr = []
already_ids = []

api = 'http://api.douban.com/v2/movie/subject/%s?apikey=088ae3d5d4f3828e19a0ab817eda87aa'
r = re.compile(r'[1-9]\d+')

cookie = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))


def http_get(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36'
    }

    try:
        req = urllib2.Request(url, headers=headers)
        response = opener.open(req, timeout=20)
        # print response.info()
        content = response.read()
        content = zlib.decompress(content, 16 + zlib.MAX_WBITS)
    except urllib2.HTTPError, e:
        print 'HTTP Code: ' + str(e.code)
        logging.exception('HTTP Code: ' + str(e.code))
        if e.code == 403:
            with open('/tmp/douban.exit.log', 'a') as f:
                f.write('403Err: end ID:' + str(start_point) + "\r\n")
            sys.exit(0)
        return None
    except:
        print traceback.format_exc()
        logging.exception('http failure')
        return None
    return content


def parse(ID):
    try:
        data = http_get(api % ID)
        if not data:
            return

        js = json.loads(data)
        if int(js['id']) in already_ids:
            return

        sql = "INSERT INTO movie (" \
              "douban_movie_id, title, original_title," \
              " aka, alt, mobile_url, " \
              "rating_average, rating_stars, ratings_count," \
              " wish_count, collect_count, " \
              "images_small, images_large, images_medium, " \
              "subtype, year, summary, " \
              "comments_count, reviews_count, seasons_count, " \
              "current_season, episodes_count, add_time) " \
              "VALUES(" \
              " %s, %s, %s," \
              " %s,%s, %s," \
              " %s, %s, %s," \
              " %s, %s," \
              " %s, %s, %s," \
              " %s, %s, %s, " \
              "%s, %s, %s," \
              " %s, %s, %s" \
              ");"

        param = (
            js['id'], js['title'], js['original_title'],
            ','.join(js['aka']), js['alt'], js['mobile_url'],
            js['rating']['average'] * 10, js['rating']['stars'], js['ratings_count'],
            js['wish_count'], js['collect_count'],
            js['images']['small'], js['images']['large'],
            js['images']['medium'],
            js['subtype'], js['year'], js['summary'],
            js['comments_count'] or -1, js['reviews_count'] or -1, js['seasons_count'] or -1,
            js['current_season'] or -1, js['episodes_count'] or -1, int(time.time())
        )

        sql_arr.append((sql, param))
        if js['countries']:
            for country in js['countries']:
                sql = "INSERT INTO countrie(douban_movie_id,country) values(%s, %s);"
                sql_arr.append((sql, (js['id'], country or ' ')))

        if js['genres']:
            for genre in js['genres']:
                sql = "INSERT INTO genre(douban_movie_id,genre) values(%s, %s);"
                sql_arr.append((sql, (js['id'], genre or ' ')))

        if js['directors']:
            for director in js['directors']:
                if director['id']:
                    sql = "INSERT INTO director(douban_director_id,name,alt,small,large,medium) values(%s, %s ,%s ,%s ,%s ,%s) ON DUPLICATE KEY UPDATE name = name;"

                    small = ''
                    large = ''
                    medium = ''
                    if director['avatars']:
                        small = director['avatars']['small']
                        large = director['avatars']['large']
                        medium = director['avatars']['medium']

                    sql_arr.append((sql, (
                        director['id'], director['name'] or ' ', director['alt'] or ' ', small or ' ',
                        large or ' ', medium or ' ')))

                    sql = "INSERT INTO movie_director_map(douban_movie_id,douban_director_id) values(%s, %s);"
                    sql_arr.append((sql, (js['id'], director['id'])))

        if js['casts']:
            for cast in js['casts']:
                if cast['id']:
                    sql = "INSERT INTO `cast`(douban_cast_id,name,alt,small,large,medium) values(%s, %s ,%s ,%s ,%s ,%s) ON DUPLICATE KEY UPDATE name = name;"

                    small = ''
                    large = ''
                    medium = ''
                    if cast['avatars']:
                        small = cast['avatars']['small']
                        large = cast['avatars']['large']
                        medium = cast['avatars']['medium']

                    sql_arr.append((sql, (
                        cast['id'], cast['name'] or ' ', cast['alt'] or ' ', small or ' ',
                        large or ' ', medium or ' ')))

                    sql = "INSERT INTO movie_cast_map(douban_movie_id,douban_cast_id) values(%s, %s);"
                    sql_arr.append((sql, (js['id'], cast['id'])))
    except:
        logging.exception('parse failure')
        with open('/tmp/douban.log', 'a') as f:
            f.write(str(ID) + "\r\n")
        print traceback.format_exc()


while True:
    cur.execute("select url from url_pool limit %s,%s" % (start_point, increase))
    result = cur.fetchall()

    if not result:
        with open('/tmp/douban.exit.log', 'a') as f:
            f.write('Not result: end ID:' + str(start_point) + "\r\n")
        cur.close()
        sys.exit()

    for row in result:
        # parse(row[0])
        ID = r.findall(row[0])[0]
        if ID not in already_ids:
            already_ids.append(ID)
            start_parse_time = time.time()
            # print ID
            parse(ID)
            # print 'end'
            if (time.time() - start_parse_time) < 1.5:
                time.sleep(1.5)

    start_point += increase
    # time.sleep(sleep_s)

    try:
        line = sql_arr.pop()
        while line:
            if line:
                cur.execute(line[0], line[1])

            if sql_arr:
                line = sql_arr.pop(0)
            else:
                break

    except:
        try:
            with open('/tmp/douban.log', 'a') as ff:
                sss = ''
                for ss in line[1]:
                    sss += str(ss) + ','

                ff.write(line[0] + '-----------------' + sss + "\r\n")
        except:
            pass

        logging.exception('sql execute failure')
        print traceback.format_exc()
        print (line[0], line[1])

print (time.time() - start_time) * 1000


