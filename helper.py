# coding=utf-8
import random
import time
import urllib2
import json
import sys
import requests
import zlib
import base64
import socket
import copy
from functions import smarty_encode, get_domain, md5

from mongo_single import Mongo
# from functions import socket_client
from contextlib import closing

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
        self.__init_format = {
            '_id': '',
            'ip': '',
            'parsed_count': 0,
            'connected_count': 0,
            'last_connected_time': 0,
            'work_time_count': 1,
            'deny_domains': [],
            'error_domains': {},
            'static': '抓取中'}
        self.slave_record = {}

        self.deny_urls_temp = {}

        if not self.slave_record:
            for item in Mongo.get().slave_record.find():
                item['data']['_id'] = str(item['_id'])
                item['data']['ip'] = str(item['ip'])
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
        """
        if ip not in self.slave_record:
            self.slave_record[ip] = copy.deepcopy(self.__init_format)

    def add_parsed_record(self, ip):
        self.__init_key(ip)
        self.slave_record[ip]['parsed_count'] += 1

    def add_fails_record(self, ip, fails=()):
        """
        根据失败的url抓取记录且一定时间达到一定数量则将url加入该slave (IP)的禁止名单中
        """
        self.__init_key(ip)
        start_time = int(time.time()) - 30 * 60  # 半小时前
        start_time_clean = int(time.time()) - 120 * 60  # 两个小时前

        # 判断时间清理掉一段时间之前的禁止名单
        deny_domains = []
        deny_domains_temp = copy.deepcopy(self.slave_record[ip]['deny_domains'])  # 深复制
        for item in deny_domains_temp:
            deny_domains.append(item['domain'])

            if item['add_time'] < start_time_clean:  # 如果是指定时间之前添加的则清除掉该slave (IP)禁止名单
                self.slave_record[ip]['deny_domains'].remove(item)

        for item in fails:
            domain = item[0]
            http_code = int(item[1])
            add_time = item[2]

            if http_code == 403 and domain not in deny_domains:
                self.deny_urls_temp.setdefault(ip, {})
                res = self.deny_urls_temp[ip].setdefault(domain, {'count': 0, 'time': []})
                self.deny_urls_temp[ip][domain]['count'] += 1
                self.deny_urls_temp[ip][domain]['time'].append(add_time)

                # 403 一定时间达到一定次数就加禁止入名单
                if res['count'] == 10:

                    # 半小时内达到一定次数
                    time_count = 0
                    for t in self.deny_urls_temp[ip][domain]['time']:
                        if t > start_time:
                            time_count += 1
                    if time_count < 10:  # 未达到次数下限
                        continue

                    # 加入禁止名单和清空临时数据
                    self.slave_record[ip]['deny_domains'].append({'domain': domain, 'add_time': int(time.time())})
                    del self.deny_urls_temp[ip]
                    continue

            # 其他非403的处理
            if http_code != 403:
                domain_md5 = md5(domain)  # mongoDB不支持带.的key
                self.slave_record[ip]['error_domains'].setdefault(domain_md5, {})
                self.slave_record[ip]['error_domains'][domain_md5].setdefault('domain', domain)
                self.slave_record[ip]['error_domains'][domain_md5].setdefault('add_time', int(time.time()))
                self.slave_record[ip]['error_domains'][domain_md5]['update_time'] = int(time.time())
                self.slave_record[ip]['error_domains'][domain_md5].setdefault('http_code', {})
                self.slave_record[ip]['error_domains'][domain_md5]['http_code'].setdefault(str(http_code), 0)
                self.slave_record[ip]['error_domains'][domain_md5]['http_code'][str(http_code)] += 1
                continue


    def add_request_record(self, ip):
        self.__init_key(ip)
        self.slave_record[ip]['connected_count'] += 1
        self.__set_connect_record(ip)
        self.refresh_connect_status()

        # todo 不能每次实时插入 或者 web端获取时不通过 process.Manager 的方式获取,改用mongoDB获取
        self.__storage_record()

    def refresh_connect_status(self):
        now = int(time.time())

        global_slave_record = GlobalHelper.get('salve_record')
        if not global_slave_record:
            global_slave_record = self.slave_record

        for k, item in global_slave_record.items():
            leave_second = now - item['last_connected_time']
            if leave_second > 60 * 60:  # 失联1小时以上
                self.slave_record[k]['static'] = u'已丢失'
            elif leave_second > 60 * 10:  # 失联10分钟以上
                self.slave_record[k]['static'] = u'断开中'
            elif global_slave_record[k]['static'] == '暂停中':
                self.slave_record[k]['static'] = u'暂停中'
            else:
                self.slave_record[k]['static'] = u'抓取中'

    def __set_connect_record(self, ip):
        now = int(time.time())
        last_connected_time = self.slave_record[ip]['last_connected_time']
        self.slave_record[ip]['last_connected_time'] = now

        if now - last_connected_time < 60 * 10:  # fixme 0时会不计算
            self.slave_record[ip]['work_time_count'] += now - last_connected_time

    def __storage_record(self):
        for ip, data in self.slave_record.items():
            res = Mongo.get().slave_record.update(
                {'ip': ip},
                {'ip': ip, 'data': data}, True)  # 有着更新, 无则插入

            if not res['updatedExisting'] and 'upserted' in res:  # 插入时
                self.slave_record[ip]['_id'] = str(res['upserted'])


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
        self.domain = ''
        self.domain_crawl_history = {}
        self.requester = None
        self.user_agent = ''

    def __init_domain_crawl_history_keys(self):
        self.domain_crawl_history.setdefault(self.domain, {
            'user_agent_counter': 0,
            'requester_counter': 0,
            'last_url': '',
        })

    def get_requester(self):
        """
        获取固定会话信息的requester
        在执行若干次后会更新cookie, 一定几率降低被封可能
        """
        self.__init_domain_crawl_history_keys()

        if self.domain_crawl_history[self.domain]['requester_counter'] >= 20 or not self.requester:
            self.requester = requests.Session()
            self.domain_crawl_history[self.domain]['requester_counter'] = 0

        self.domain_crawl_history[self.domain]['requester_counter'] += 1
        return self.requester

    def get_refer_url(self):
        self.__init_domain_crawl_history_keys()
        last_url = self.domain_crawl_history[self.domain]['last_url']
        self.domain_crawl_history[self.domain]['last_url'] = self.url  # 获取后会更新
        return last_url

    def get_headers(self):
        """
        以该域名的上次一次访问url做为Referer
        随机获取user_agent
        """
        user_agent = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.' + str(random.randint(10, 99)) +
            ' (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240 ' + str(random.randint(10, 99)),
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.' + str(random.randint(10, 99)) +
            ' (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36 ' + str(random.randint(10, 99)),
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.' +
            str(random.randint(10, 99)) + ' Safari/537.' + str(random.randint(10, 99)),
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.' + str(random.randint(10, 99)) +
            ' (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.' + str(random.randint(10, 99)),
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko ' + str(random.randint(10, 99))
        ]

        accept = [
            'text/html, application/xhtml+xml, image/jxr, */*',
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        ]

        base_url = "".join(self.url.split())
        protocol, rest = urllib2.splittype(base_url)
        host, rest = urllib2.splithost(rest)

        if self.domain_crawl_history[self.domain]['user_agent_counter'] >= 15 or not self.user_agent:
            self.user_agent = random.choice(user_agent)
            self.domain_crawl_history[self.domain]['user_agent_counter'] = 0

        self.domain_crawl_history[self.domain]['user_agent_counter'] += 1

        headers = {
            'Host': host,
            'Accept': random.choice(accept),
            # 'Pragma': 'no-cache',
            # 'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': self.user_agent,
        }

        # headers_ms_edge = {
        # 'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        # 'Accept-Language': 'zh-Hans-CN,zh-Hans;q=0.5',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'+
        # ' (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240 1235',
        # 'Accept-Encoding': 'gzip, deflate',
        # 'Host': host,
        # 'Connection': 'Keep-Alive',
        # }
        #
        # headers = headers_ms_edge

        # print headers

        # 以该域名的上次一次访问url做为refer
        refer_url = self.get_refer_url()
        if refer_url:
            headers['Referer'] = refer_url

        return headers

    # def post(self, url, params=()):
    # return self.__request('post', url, params)

    def get(self, url, params=()):
        self.domain = get_domain(url)
        self.url = url
        return self.__request('get', params)

    def __request(self, method, params=()):
        start_time = time.time()
        try:
            content = ''

            if method == 'post':
                req = self.get_requester().post(self.url, headers=self.get_headers(), timeout=10, params=params)
                if not req.encoding == 'utf-8':
                    req.encoding = 'utf-8'

            else:
                with closing(self.get_requester().get(self.url, headers=self.get_headers(), timeout=10, params=params,
                                                      allow_redirects=True, stream=True)) as req:
                    # if not req.encoding == 'utf-8':
                    # req.encoding = 'utf-8'

                    # print req.headers
                    size_limit = 1024000  # 最大接收content-length
                    if 'content-length' in req.headers:
                        if int(req.headers['content-length']) > size_limit:
                            raise Exception(
                                'content-length too many. content-length: ' + str(req.headers['content-length']))

                        content = req.content

                    else:
                        size_temp = 0
                        for line in req.iter_lines():
                            if line:
                                size_temp += len(line)
                                if size_temp > size_limit:
                                    raise Exception('content-length too many.')

                                content += line

            content = smarty_encode(content)

        except requests.ConnectionError, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        except requests.HTTPError, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        except requests.Timeout, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        except Exception, e:
            return None, str(e.message), round((time.time() - start_time) * 1000, 2)
        else:
            return str(content), req.status_code, round((time.time() - start_time) * 1000, 2)


class S:
    """
    用户自定义抓取回调时的参数对象
    """

    def __init__(self, spider, html, urls, project_name, init_url):
        self.__spider = None
        self.html = ''
        self.urls = []
        self.__spider = spider
        self.html = html
        self.project_name = project_name
        self.init_url = init_url
        self.urls = urls

    def crawl(self, url):
        self.__spider.crawl(url)


class QueueCtrl():
    """
    采用多种方式控制整个slave的抓取顺序与速度
    具体功能由之类实现
    """
    host_freq_pool = {}

    def __init__(self):
        pass

    @classmethod
    def add_parsed(cls, url):
        # 获取主域名并更新该域名的访问频率
        cls.__update_host_freq(get_domain(url))

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
    """
    根据url请求频率增加同host的url不定的sleep来控制请求速度
    """

    def __init__(self):
        QueueCtrl.__init__(self)

    @classmethod
    def get_sleep_times(cls, url):
        domain = get_domain(url)
        parsed_list = cls.host_freq_pool.get(domain, [])
        if not parsed_list:
            return 1

        list_403 = ['jandan.net', 'meizu.com', 'meizu.cn']  # 一些防爬虫机制比较严格的站点
        parsed_list_len = len(parsed_list)

        if parsed_list_len < 5:
            return 1

        if parsed_list_len < 10:
            return 1

        if parsed_list_len < 20:
            if domain in list_403:
                return random.randint(5, 20)
            return 2

        if parsed_list_len < 30:
            if domain in list_403:
                return random.randint(5, 35)
            return 4

        if parsed_list_len < 40:
            if domain in list_403:
                return random.randint(5, 40)
            return 6

        if parsed_list_len < 50:
            if domain in list_403:
                return random.randint(5, 56)
            return 8

        if parsed_list_len < 60:
            if domain in list_403:
                return random.randint(5, 70)
            return 10

        if parsed_list_len < 70:
            return 12

        if parsed_list_len < 80:
            return 14

        return 40


class UrlsSortCtrl(QueueCtrl):
    """
    将请求次数少的url排序在列表最前
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
            sorted_urls[url] = len(cls.host_freq_pool.get(get_domain(url), []))

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
            'urls_fail': [],
        }

    def __init__(self, project_name):
        self.data = {}
        self.project_name = ''
        self.project_name = project_name
        self.original_receive_json = {}
        self.last_change_time = 0
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
        if not response:
            return None

        self.original_receive_json = response
        urls = list(set(response.get('urls', [])))
        urls = UrlsSortCtrl.sort_urls_by_freq(urls)

        response['urls'] = urls

        print round((time.time() - start_time) * 1000, 2), 'ms'
        if response:
            self.__init_data()

        return response

    def put_data(self, urls_parsed=(), urls_add=(), save=(), urls_fail=()):
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

        urls_fail and self.data['urls_fail'].append(urls_fail)

        save and self.data['save'].append(save)

    def has_project_change(self):
        current_change_time = int(self.original_receive_json.get('change_time', self.last_change_time))

        if self.last_change_time == 0:
            self.last_change_time = current_change_time

        if current_change_time == self.last_change_time:
            return False

        self.last_change_time = current_change_time
        return True

    def get_origin_receive_json(self):
        return self.original_receive_json

    @classmethod
    def __request_server(cls, data):
        response = None
        try:
            json_string = Socket_client.run(json.dumps(data))
            response = json.loads(json_string)
        finally:
            return response


class Socket_client:
    host = ''
    port = 0

    @classmethod
    def set_host(cls, host):
        cls.host = host

    @classmethod
    def set_port(cls, port):
        cls.port = port

    @classmethod
    def run(cls, content):
        """
        Slave与Master的socket通讯client端
        使用特定格式传输
        传输时会压缩数据
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((cls.host, cls.port))

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