# coding=utf-8
import zlib
import base64
import socket
import requests
import random
import time
import json
import sys
from mongo_single import Mongo

reload(sys)
sys.setdefaultencoding('utf8')


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
    slave_record = {}
    __init_format = {'parsed_count': 0, 'connected_count': 0, 'last_connected_time': 0, 'work_time_count': 1,
                     'static': '抓取中'}

    def __init__(self):
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
    url = ''
    host_url = ''
    num = 0
    requester = None

    def __init__(self):
        pass

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

        except requests.ConnectionError, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        except requests.HTTPError, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        except requests.Timeout, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        except Exception, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        else:
            return req.text, req.status_code, round((time.time() - start_time) * 1000, 2)


class SlaveForDev():
    def __init__(self):
        pass

    def get_data(self):
        pass

    def put_data(self, urls_parsed=(), urls_add=(), save=()):
        pass


class Slave():
    """
    slave与master数据传输对象
    使用特定格式传输
    传输时会压缩数据
    """
    data = {}
    project_name = ''

    def __init_data(self):
        self.data = {
            'project_name': self.project_name,
            'get_urls': 1,
            'urls_parsed': [],
            'urls_add': [],
            'save': [],
        }

    def __init__(self, project_name):
        self.project_name = project_name
        self.__init_data()

    def get_data(self):
        """
        获取master中的新url队列, 并把之前缓存的所有数据推送至master
        :return:
        """
        self.data['urls_add'] = list(set(self.data['urls_add']))  # queue 去重

        start_time = time.time()

        response = self.__request(self.data)
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
            self.data['urls_parsed'].append(url)

        for url in urls_add:
            self.data['urls_add'].append(url)

        if save:
            self.data['save'].append(save)

    @classmethod
    def __request(cls, data):
        response = None
        try:
            json_string = cls.socket_client(json.dumps(data))
            response = json.loads(json_string)
        finally:
            return response

    @staticmethod
    def socket_client(content):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 7777))

        send_date = base64.b64encode(zlib.compress(content))  # 压缩编码

        # content前10个字符串用于标识内容长度.
        response_len = (str(len(send_date) + 10) + ' ' * 10)[0:10]
        sock.sendall(response_len + send_date)
        buff_size = 1024
        data = sock.recv(buff_size)

        # content前10个字符串用于标识内容长度.
        data_len = int(data[0:10])
        while len(data) < data_len:
            s = sock.recv(buff_size)
            data += s

        data = zlib.decompress(base64.b64decode(data[10:]))  # 解码解压

        sock.close()

        return data