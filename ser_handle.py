# coding=utf-8
import time
import pymongo
from mongo_single import Mongo
from functions import md5
import sys
from gevent.lock import BoundedSemaphore

reload(sys)
sys.setdefaultencoding('utf8')

sem = BoundedSemaphore()


class SerHandle():
    __request_json = {}
    __request_address = []

    def __init__(self, request_json, request_address):
        self.__request_json = request_json
        self.__request_address = request_address

    def get_urls(self):
        # sem.acquire()
        # urls_add_start_time = time.time()
        response_url_list = []
        ids = []
        for doc in Mongo.get().queue.find({'flag_time': {'$lt': int(time.time() - 300)}}).limit(
                10).sort('_id', pymongo.ASCENDING):  # 取标识时间早于当前时间300秒之前的url
            ids.append(doc['_id'])
            response_url_list.append(doc['url'])

        # todo 没有地址的情况下给一个  test !!
        # if not response_url_list:
        #     try:
        #         tmp_url = 'http://jandan.net/'
        #         response_url_list.append(tmp_url)
        #         ids.append(Mongo.get().queue.insert(
        #             {'url': tmp_url, 'url_md5': md5(tmp_url), 'flag_time': 0, 'add_time': int(time.time()),
        #              'slave_ip': self.__request_address[0]}))
        #     except:
        #         pass

        # todo 多线程情况下, 这里线程非安全
        ids and Mongo.get().queue.update({'_id': {'$in': ids}}, {'$set': {'flag_time': int(time.time())}},
                                         multi=True)
        # print 'get time', round((time.time() - urls_add_start_time) * 1000, 2), ' ms'
        # sem.release()
        return response_url_list

    def urls_add(self):
        urls_add_start_time = time.time()
        add_url_list = list(set(self.__request_json['urls_add']))  # 去重

        # 已存在queue中的
        exist_queue_url_list = []
        res = Mongo.get().queue.find({'url_md5': {'$in': [md5(l) for l in add_url_list]}}, {'url': 1})

        for doc in res:
            exist_queue_url_list.append(doc['url'])

        # 已存在parsed中的
        exist_parsed_url_list = []

        res = Mongo.get().parsed.find({'url_md5': {'$in': [md5(l) for l in add_url_list]}}, {'url': 1})
        for doc in res:  # todo 需要判断存在的时间, 允许重复抓取
            exist_parsed_url_list.append(doc['url'])

        # 加入队列
        add_urls_data = []
        for url in add_url_list:
            if url not in exist_queue_url_list and url not in exist_parsed_url_list:  # 不存在queue不存在parsed中才加入队列
                add_urls_data.append({'url': url, 'url_md5': md5(url), 'flag_time': 0, 'add_time': int(time.time()),
                                      'slave_ip': self.__request_address[0]})

        add_urls_data and Mongo.get().queue.insert(add_urls_data)
        print 'add time', round((time.time() - urls_add_start_time) * 1000, 2), ' ms'

    def urls_parsed(self):
        # urls_add_start_time = time.time()
        urls_data = []
        url_list = []
        for url in self.__request_json['urls_parsed']:
            url_list.append(url)
            urls_data.append(
                {'url': url, 'url_md5': md5(url), 'add_time': int(time.time()), 'slave_ip': self.__request_address[0]})

        Mongo.get().queue.remove({'url_md5': {'$in': [md5(l) for l in url_list]}}, multi=True)  # 删除抓取完毕的队列
        urls_data and Mongo.get().parsed.insert(urls_data)
        # print 'parsed time', round((time.time() - urls_add_start_time) * 1000, 2), ' ms'

    def result_save(self):
        # urls_add_start_time = time.time()
        Mongo.get().result.insert(self.__request_json['save'])
        # print 'save time', round((time.time() - urls_add_start_time) * 1000, 2), ' ms'