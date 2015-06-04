# coding=utf-8
import requests
import urllib2
import random

import time

import json

import sys

from mongo_single import Mongo
from functions import socket_client
from tld import get_tld

reload(sys)
sys.setdefaultencoding('utf-8')


class SlaveRecord():
    """
    记录每个slave的
    1.解析量
    2.通讯次数
    3.上次通讯时间
    4.在线时长

    该对象为单例, 请勿实例化. 请使用get方法获取实例
    """
    __instance = None

    def __init__(self):
        self.__init_format = {'parsed_count': 0, 'connected_count': 0, 'last_connected_time': 0, 'work_time_count': 1,
                              'static': '抓取中'}
        self.slave_record = {}

        if not self.slave_record:
            for item in Mongo.get().slave_record.find():
                self.slave_record[item['ip']] = item['data']

        self.refresh_connect_status()

    @classmethod
    def get_instance(cls):
        """
        单例获取方法
        """
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def __init_key(self, ip):
        """
        避免key未初始化而报错的问题
        应该有更优雅的方式
        """
        if ip not in self.slave_record:
            self.slave_record[ip] = dict(self.__init_format)

    def add_parsed_record(self, ip):
        self.__init_key(ip)
        self.slave_record[ip]['parsed_count'] += 1

    def add_request_record(self, ip):
        self.__init_key(ip)
        self.slave_record[ip]['connected_count'] += 1
        self.__set_connect_record(ip)
        self.refresh_connect_status()

        # todo 不能每次实时插入 或者 web端获取时不通过 process.Manager 的方式获取,改用mongoDB获取
        self.__storage_record()

    def refresh_connect_status(self):
        now = int(time.time())
        for k, item in self.slave_record.items():
            leave_second = now - item['last_connected_time']
            if leave_second > 60 * 60:  # 失联1小时以上
                self.slave_record[k]['static'] = '已丢失'
            elif leave_second > 60 * 10:  # 失联10分钟以上
                self.slave_record[k]['static'] = '断开中'
            else:
                self.slave_record[k]['static'] = '抓取中'

    def __set_connect_record(self, ip):
        now = int(time.time())
        last_connected_time = self.slave_record[ip]['last_connected_time']
        self.slave_record[ip]['last_connected_time'] = now

        if now - last_connected_time < 60 * 10:  # fixme 0时会不计算
            self.slave_record[ip]['work_time_count'] += now - last_connected_time

    def __storage_record(self):
        for ip, data in self.slave_record.items():
            Mongo.get().slave_record.update(
                {'ip': ip},
                {'ip': ip, 'data': data}, True)  # 有着更新, 无则插入

    def __del__(self):
        self.__storage_record()


class GlobalHelper:
    """
    跨进程间的变量共享工具
    依赖 multiprocessing.Manger
    """
    __source_data = {}

    @classmethod
    def init(cls, d):
        """
        需要特殊的初始化过程, 详见调用处
        设置跨进程的引用变量
        """
        cls.__source_data = d

    @classmethod
    def get(cls, key):
        if key not in cls.__source_data:
            return

        return cls.__source_data[key]

    @classmethod
    def set(cls, key, value):
        """
        每次跨进程都要重新set, init只需要一次,set是每次
        """
        cls.__source_data[key] = value


class HttpHelper():
    """
    基于requests再次封装的http请求对象
    """

    def __init__(self):
        self.url = ''
        self.host_url = ''
        self.num = 0
        self.requester = None

    def get_requester(self):
        """
        获取固定会话信息的requester
        在执行若干次后会更新cookie, 一定几率降低被封可能
        """
        if self.num >= 30 or not self.requester:
            self.requester = requests.session()
            self.num = 0

        self.num += 1
        return self.requester

    @staticmethod
    def get_headers():
        """
        每次随机获取header, 一定几率降低被封可能
        """
        user_agent = [
            'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 ' +
            '(KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 ' +
            '(KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
        ]
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': random.choice(user_agent),
        }

    def post(self, url, params=()):
        return self.__request('post', url, params)

    def get(self, url, params=()):
        return self.__request('get', url, params)

    def __request(self, method, url, params=()):

        self.url = url

        start_time = time.time()
        try:
            if method == 'post':
                req = self.get_requester().post(self.url, headers=self.get_headers(), timeout=10, params=params)
            else:
                req = self.get_requester().get(self.url, headers=self.get_headers(), timeout=10, params=params)

            if not req.encoding == 'utf-8':
                req.encoding = 'utf-8'

        except requests.ConnectionError, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        except requests.HTTPError, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        except requests.Timeout, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        except Exception, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        else:
            return str(req.text), req.status_code, round((time.time() - start_time) * 1000, 2)


class S:
    """
    用户自定义抓取回调时的参数对象
    """

    def __init__(self, spider, html, urls):
        self.__spider = None
        self.html = ''
        self.urls = []
        self.__spider = spider
        self.html = html
        self.urls = urls

    def crawl(self, url):
        self.__spider.crawl(url)


class QueueCtrl():
    host_freq_pool = {}

    def __init__(self):
        pass

    @classmethod
    def add_parsed(cls, url):
        # 获取主域名并更新该域名的访问频率
        cls.__update_host_freq(get_tld(url))
        # cls.parsed_url_pool.append((url, int(time.time())))

    @classmethod
    def __update_host_freq(cls, host):
        """
        更新域名的访问频率
        """
        cls.host_freq_pool.setdefault(host, [])
        cls.host_freq_pool[host].append(int(time.time()))

    @classmethod
    def clear_host_freq_pool(cls, expire=300):
        """
        整理host_freq_pool

        过滤掉根域名对应的访问时间戳列表中访问时间超出给定值的时间戳
        or
        删除pool长度为0的host
        or
        删除pool长度大于1000的部分
        """
        now = int(time.time())
        for host, pool in cls.host_freq_pool.items():
            # 过多时删除部分
            pool_len = len(cls.host_freq_pool[host])
            if pool_len > 1000:
                del cls.host_freq_pool[host][0:500]
            elif pool_len == 0:
                del cls.host_freq_pool[host]

            for timestamp in list(pool):
                if now - timestamp > expire:
                    cls.host_freq_pool[host].remove(timestamp)
                else:
                    break


class QueueSleepCtrl(QueueCtrl):
    def __init__(self):
        QueueCtrl.__init__(self)

    @classmethod
    def sleep(cls, urls):
        # yield urls
        return urls


class UrlsSortCtrl(QueueCtrl):
    """
    采用多种方式控制整个slave的抓取顺序与速度
    """

    def __init__(self):
        QueueCtrl.__init__(self)

    @classmethod
    def sort_urls_by_freq(cls, urls):
        """
        根据host抓取次数排序urls
        """
        sorted_urls = {}
        for url in urls:
            sorted_urls[url] = len(cls.host_freq_pool.get(get_tld(url), []))
        return cls.__sort_dict_by_value_return_keys(sorted_urls)

    @classmethod
    def __sort_dict_by_value_return_keys(cls, d):
        """
        根据value顺序返回keys
        用于根据host抓取次数排序urls
        """
        l = []
        temp = d.items()
        for value in sorted(d.values()):
            index = 0
            for k, v in temp:
                if v == value:
                    l.append(k)
                    del temp[index]
                    index += 1
                    break
                index += 1
        return l


class Slave():
    def __init_data(self):
        self.data = {
            'project_name': self.project_name,
            'get_urls': 1,
            'urls_parsed': [],
            'urls_add': [],
            'save': [],
        }

    def __init__(self, project_name):
        self.data = {}
        self.project_name = ''
        self.project_name = project_name
        self.__init_data()

    def get_data(self):
        """
        获取master中的新url队列, 并把之前缓存的所有数据推送至master
        :return:
        """
        self.data['urls_add'] = list(set(self.data['urls_add']))  # queue 去重

        start_time = time.time()

        QueueCtrl.clear_host_freq_pool()
        response = self.__request_server(self.data)
        urls = list(set(response.get('urls', [])))
        urls = UrlsSortCtrl.sort_urls_by_freq(urls)
        response['urls'] = urls

        print round((time.time() - start_time) * 1000, 2), 'ms'
        if response:
            self.__init_data()

        return response

    def put_data(self, urls_parsed=(), urls_add=(), save=()):
        """
        不会真正推送数据, 只先加入缓存属性中, 当执行self.get_data时再一并推送
        :param urls_parsed:
        :param urls_add:
        :param save:
        :return:
        """
        for url in urls_parsed:
            QueueCtrl.add_parsed(url)
            self.data['urls_parsed'].append(url)

        for url in urls_add:
            self.data['urls_add'].append(url)

        if save:
            self.data['save'].append(save)

    @classmethod
    def __request_server(cls, data):
        response = None
        try:
            json_string = socket_client(json.dumps(data))
            response = json.loads(json_string)
        finally:
            return response