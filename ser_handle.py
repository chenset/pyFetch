# coding=utf-8
import urllib2
import time
import pymongo
from functions import get_domain

from mongo_single import Mongo
from functions import md5
import sys
import traceback
from helper import SlaveRecord

reload(sys)
sys.setdefaultencoding('utf8')


class SerHandle():
    def __init__(self, project_name, request_json, request_address):
        self.project_name = project_name
        temp = list(
            Mongo.get()['projects'].find({'name': self.project_name}).limit(1))
        self.project = temp[0] if temp else []
        self.__request_json = request_json
        self.__request_address = request_address
        self.__slave_record = SlaveRecord.get_instance()

    def get_project(self):
        return self.project

    def get_urls(self):
        # SerHandle.__init_project(self.project_name)
        response_url_list = []
        ids = []
        # print self.__slave_record.slave_record[self.__request_address[0]]['deny_domains']

        # todo need to test
        deny_domains = [x['domain'] for x in
                        self.__slave_record.slave_record[self.__request_address[0]]['deny_domains']]

        for doc in Mongo.get()['queue_' + self.project_name].find(
                {'domain': {'$nin': deny_domains}, 'flag_time': {'$lt': int(time.time() - 300)}}).limit(20) \
                .sort('_id', pymongo.ASCENDING):  # 取标识时间早于当前时间300秒之前的url
            ids.append(doc['_id'])
            response_url_list.append(doc['url'])

        # todo 多线程情况下, 这里线程非安全
        ids and Mongo.get()['queue_' + self.project_name].update({'_id': {'$in': ids}},
                                                                 {'$set': {'flag_time': int(time.time())}},
                                                                 multi=True)
        return response_url_list

    def urls_add(self):
        add_url_list = list(set(self.__request_json['urls_add']))  # 去重

        # 已存在queue中的
        exist_queue_url_list = []
        res = Mongo.get()['queue_' + self.project_name].find({'url_md5': {'$in': [md5(l) for l in add_url_list]}},
                                                             {'url': 1})

        for doc in res:
            exist_queue_url_list.append(doc['url'])

        # 已存在parsed中的
        exist_parsed_url_list = []

        res = Mongo.get()['parsed_' + self.project_name].find({'url_md5': {'$in': [md5(l) for l in add_url_list]}},
                                                              {'url': 1})
        for doc in res:  # todo 需要判断存在的时间, 允许重复抓取
            exist_parsed_url_list.append(doc['url'])

        # 加入队列
        add_urls_data = []
        for url in add_url_list:
            if url not in exist_queue_url_list and url not in exist_parsed_url_list:  # 不存在queue不存在parsed中才加入队列
                add_urls_data.append(
                    {'domain': get_domain(url),
                     'url': url,
                     'url_md5': md5(url),
                     'flag_time': 0,
                     'add_time': int(time.time()),
                     'slave_ip': self.__request_address[0]})

        add_urls_data and Mongo.get()['queue_' + self.project_name].insert(add_urls_data)

    def urls_parsed(self):
        urls_data = []
        url_list = []
        for url in self.__request_json['urls_parsed']:
            self.__slave_record.add_parsed_record(self.__request_address[0])
            url_list.append(url)
            urls_data.append(
                {'url': url, 'url_md5': md5(url), 'add_time': int(time.time()), 'slave_ip': self.__request_address[0]})

        Mongo.get()['queue_' + self.project_name].remove({'url_md5': {'$in': [md5(l) for l in url_list]}},
                                                         multi=True)  # 删除抓取完毕的队列

        try:
            urls_data and Mongo.get()['parsed_' + self.project_name].insert(urls_data)
        except:
            try:
                for single_url in urls_data:
                    single_url and Mongo.get()['parsed_' + self.project_name].insert_one(single_url)
            except Exception, error:
                print traceback.format_exc()
                print error
                print u'下面链接重复抓取的并重复保存到parsed_*中的记录'
                print single_url

    def result_save(self):
        Mongo.get()['result_' + self.project_name].insert(self.__request_json['save'])