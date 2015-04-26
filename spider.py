# coding=utf-8
import requests
import random
import time
import json
import sys
import urllib2

reload(sys)
sys.setdefaultencoding('utf8')
from socket_client import socket_client


def echo_err(msg):
    sys.stderr.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' ' + msg + '\r\n')


class Crawl():
    url = ''
    host_url = ''
    num = 0
    requester = None

    def __init__(self):
        pass

    def get_requester(self):
        if self.num >= 30 or not self.requester:
            self.requester = requests.session()
            self.num = 0

        self.num += 1
        return self.requester

    @staticmethod
    def get_headers():
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


class DataKit():
    data = {}

    def __init_data(self):
        self.data = {
            'get_urls': 1,
            'urls_parsed': [],
            'urls_add': [],
            'save': [],
        }

    def __init__(self):
        self.__init_data()

    def get_data(self):
        self.data['urls_add'] = list(set(self.data['urls_add']))  # queue 去重

        start_time = time.time()
        response = self.__request(self.data)
        print round((time.time() - start_time) * 1000, 2), 'ms'
        if response:
            self.__init_data()

        return response

    def put_data(self, urls_parsed=(), urls_add=(), save=()):
        for url in urls_parsed:
            self.data['urls_parsed'].append(url)

        for url in urls_add:
            self.data['urls_add'].append(url)

        if save:
            self.data['save'].append(save)

    @staticmethod
    def __request(data):
        try:
            json_string = socket_client(json.dumps(data))
            response = json.loads(json_string)
        except:
            return None
        else:
            return response


class Spider:
    handle_method = None
    DataKit = None
    pre_url_queue = []
    Crawl = None
    current_url = ''  # 当前url

    def __init__(self):
        self.DataKit = DataKit()
        self.Crawl = Crawl()

    @staticmethod
    def __get_url_host(url):
        protocol, rest = urllib2.splittype(url)
        host, rest = urllib2.splithost(rest)

        return protocol + "://" + host

    def run(self, func):
        self.handle_method = func
        while True:
            # todo 需要些速度控制方法.
            # todo 需要判断header, 避免下载文件
            self.current_url = self.__get_queue_url()
            print self.current_url
            if not self.current_url:
                # break
                continue
            crawl_result = self.Crawl.get(self.current_url)
            self.DataKit.put_data(urls_parsed=[self.current_url, ])
            if crawl_result[1] not in (200, 201):
                echo_err(
                    'URL: ' + self.current_url + ' 获取失败 HTTP code: ' + str(crawl_result[1]) + ' Runtime: ' + str(
                        crawl_result[2]) + 'ms')
                # break
                continue

            # 如果抓取自定义函数存在dict返回值则将dict推送至服务器
            parse_result = self.handle_method(crawl_result[0])
            if not isinstance(parse_result, dict):
                # break
                continue

            if 'url' not in parse_result:
                parse_result['url'] = self.current_url
            if 'runtime' not in parse_result:
                parse_result['runtime'] = crawl_result[2]

            self.DataKit.put_data(save=parse_result)

    def crawl(self, url=''):
        """
        仅加入远程待抓取队列
        self.run()会死循环的从本地队列中获取url进行实际抓取
        :param string url:
        :return:
        """
        # 转换非完整的url格式
        if url.startswith('.'):  # 以点开头的相对url地址
            url = self.current_url.rstrip('/') + "/" + url.lstrip('./')
        elif url.startswith('/'):  # 以根开头的绝对url地址
            url = self.__get_url_host(self.current_url).rstrip('/') + "/" + url.lstrip('/')

        self.DataKit.put_data(urls_add=(url,))

    def __get_queue_url(self):
        """
        每次从本地队列返回一条将要抓取的url
        如果本地队列为空则去远程获取, 当远程获取失败会sleep数秒后重试直到成功
        远程获取的过程如果失败会因为等待重试的sleep而阻塞
        :return:string url|None
        """
        while not self.pre_url_queue:
            response = self.DataKit.get_data()
            if not response:
                echo_err('远程响应异常, 60秒后重试')
                time.sleep(60)
                continue

            if 'urls' not in response or not response['urls']:
                echo_err('无法从远程获取url队列, 10秒后重试 ' + response['msg'] or '')
                time.sleep(10)
                continue

            self.pre_url_queue += response['urls']

        return self.pre_url_queue.pop(0)  # 出栈首位