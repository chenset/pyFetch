# coding=utf-8
import requests
import random
import time
import json


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
            'User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
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
        return self.request('post', url, params)

    def get(self, url, params=()):
        return self.request('get', url, params)

    def request(self, method, url, params=()):

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
        else:
            return req.text, req.status_code, round((time.time() - start_time) * 1000, 2)


class DataKit():
    sock = None

    def __init__(self):
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        # self.sock.connect(('172.16.16.99', 9999))
        pass

    def get_patterns(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.connect(('121.40.78.16', 9999))
        data = {
            'username': 'dsfsdfsdf',
            'password': 'fgdgd_fdsf_fdsf.gfd',
            'function': {
                'method': 'get_patterns',
            }
        }

        try:
            sock.send(json.dumps(data) + 'end[\ddd*&^@#$')
            json_string = sock.recv(1024)
            response = json.loads(json_string)
        except:
            print traceback.format_exc()
            sock.close()
            return None

        if not bool(response['success']):
            print response['msg']  # 失败处理
            sock.close()
            return None

        if not response.has_key('scan_url'):
            print '------------------------ get_patterns ----------- start -------------'
            print response
            print '------------------------ get_patterns ----------- end ---------------'
            sock.close()
            return None
        sock.close()
        return response

    def get_data(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.connect(('121.40.78.16', 9999))

        data = {
            'username': 'dsfsdfsdf',
            'password': 'fgdgd_fdsf_fdsf.gfd',
            'function': {
                'method': 'get',
            }
        }

        try:
            sock.send(json.dumps(data) + 'end[\ddd*&^@#$')
            json_string = sock.recv(1024)
            response = json.loads(json_string)
        except:
            print traceback.format_exc()
            sock.close()
            return None

        if not bool(response['success']):
            print response['msg']  # 失败处理
            return None

        if not response.has_key('url'):
            print '------------------------ get_data ----------- start -------------'
            print response
            print '------------------------ get_data ----------- end ---------------'
            sock.close()
            return None

        sock.close()
        return response['url']

    def put_data(self, parsed, urls_queue, matched=()):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.connect(('121.40.78.16', 9999))

        data = {
            'username': 'dsfsdfsdf',
            'password': 'fgdgd_fdsf_fdsf.gfd',
            'function': {
                'method': 'put',
                'urls_parsed': [],
                'urls_queue': [],
                'urls_matched': [],
            }
        }

        for url in parsed:
            data['function']['urls_parsed'].append(url)

        for url in urls_queue:
            data['function']['urls_queue'].append(url)

        for url in matched:
            data['function']['urls_matched'].append(url)

        # print data
        try:
            sock.send(json.dumps(data) + 'end[\ddd*&^@#$')
            json_string = sock.recv(1024)
            response = json.loads(json_string)
        except:
            print traceback.format_exc()
            sock.close()
            return None

        if not bool(response['success']):
            print response['msg']  # 失败处理
            sock.close()
            return None

        sock.close()
        return response


class Spider:
    handle_method = {}

    def __init__(self):
        pass

    def run(self):
        if "start" not in self.handle_method:
            raise Exception('Define "start()" method first')

        self.handle_method['start']()

    def crawl(self, url):
        crawl = Crawl()
        print crawl.get(url)

    def get_url(self):
        pass

    def put_url(self):
        pass

    def start(self, func):
        self.handle_method['start'] = func

    def page(self, func):
        self.handle_method['page'] = func

    def save(self, func):
        self.handle_method['save'] = func
