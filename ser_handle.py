# coding=utf-8
import time
import pymongo
from mongo_single import Mongo
from functions import md5
import sys
# from gevent.lock import BoundedSemaphore

reload(sys)
sys.setdefaultencoding('utf8')

# sem = BoundedSemaphore()


class SerHandle():
    project_name = ''
    __request_json = {}
    __request_address = []

    def __init__(self, project_name, request_json, request_address):
        self.project_name = project_name
        self.__request_json = request_json
        self.__request_address = request_address

    __projects = []

    @classmethod
    def __init_project(cls, project_name):
        if project_name in cls.__projects:
            return

        cls.__projects.append(project_name)
        print len(cls.__projects)
        print cls.__projects

        queue_len = Mongo.get()[project_name + '_queue'].count()
        print project_name + '_queue len: ', queue_len
        print project_name + '_parsed len: ', Mongo.get()[project_name + '_parsed'].count()
        print project_name + '_result len: ', Mongo.get()[project_name + '_result'].count()
        if not queue_len:  # todo 未已经完成了所有抓取的处理
            tmp_url = 'http://jandan.net/'
            Mongo.get()[project_name + '_queue'].insert(
                {'url': tmp_url, 'url_md5': md5(tmp_url), 'flag_time': 0, 'add_time': int(time.time()),
                 'slave_ip': '0.0.0.0'})

        # 在没创建集合前设置索引mongodb会自动创建该集合并赋索引
        Mongo.get()[project_name + '_parsed'].ensure_index('url_md5', unique=True)
        Mongo.get()[project_name + '_queue'].ensure_index('url_md5', unique=True)

    def get_urls(self):
        SerHandle.__init_project(self.project_name)
        # sem.acquire()
        # urls_add_start_time = time.time()
        response_url_list = []
        ids = []
        for doc in Mongo.get()[self.project_name + '_queue'].find({'flag_time': {'$lt': int(time.time() - 300)}}).limit(
                10).sort('_id', pymongo.ASCENDING):  # 取标识时间早于当前时间300秒之前的url
            ids.append(doc['_id'])
            response_url_list.append(doc['url'])

        # todo 多线程情况下, 这里线程非安全
        ids and Mongo.get()[self.project_name + '_queue'].update({'_id': {'$in': ids}},
                                                                 {'$set': {'flag_time': int(time.time())}},
                                                                 multi=True)
        # print 'get time', round((time.time() - urls_add_start_time) * 1000, 2), ' ms'
        # sem.release()
        return response_url_list

    def urls_add(self):
        # urls_add_start_time = time.time()
        add_url_list = list(set(self.__request_json['urls_add']))  # 去重

        # 已存在queue中的
        exist_queue_url_list = []
        res = Mongo.get()[self.project_name + '_queue'].find({'url_md5': {'$in': [md5(l) for l in add_url_list]}},
                                                             {'url': 1})

        for doc in res:
            exist_queue_url_list.append(doc['url'])

        # 已存在parsed中的
        exist_parsed_url_list = []

        res = Mongo.get()[self.project_name + '_parsed'].find({'url_md5': {'$in': [md5(l) for l in add_url_list]}},
                                                              {'url': 1})
        for doc in res:  # todo 需要判断存在的时间, 允许重复抓取
            exist_parsed_url_list.append(doc['url'])

        # 加入队列
        add_urls_data = []
        for url in add_url_list:
            if url not in exist_queue_url_list and url not in exist_parsed_url_list:  # 不存在queue不存在parsed中才加入队列
                add_urls_data.append({'url': url, 'url_md5': md5(url), 'flag_time': 0, 'add_time': int(time.time()),
                                      'slave_ip': self.__request_address[0]})

        add_urls_data and Mongo.get()[self.project_name + '_queue'].insert(add_urls_data)
        # print 'add time', round((time.time() - urls_add_start_time) * 1000, 2), ' ms'

    def urls_parsed(self):
        # urls_add_start_time = time.time()
        urls_data = []
        url_list = []
        for url in self.__request_json['urls_parsed']:
            url_list.append(url)
            urls_data.append(
                {'url': url, 'url_md5': md5(url), 'add_time': int(time.time()), 'slave_ip': self.__request_address[0]})

        Mongo.get()[self.project_name + '_queue'].remove({'url_md5': {'$in': [md5(l) for l in url_list]}},
                                                         multi=True)  # 删除抓取完毕的队列
        urls_data and Mongo.get()[self.project_name + '_parsed'].insert(urls_data)
        # print 'parsed time', round((time.time() - urls_add_start_time) * 1000, 2), ' ms'

    def result_save(self):
        # urls_add_start_time = time.time()
        Mongo.get()[self.project_name + '_result'].insert(self.__request_json['save'])
        # print 'save time', round((time.time() - urls_add_start_time) * 1000, 2), ' ms'