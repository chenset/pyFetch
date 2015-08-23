# coding=utf-8
import helper
from functions import echo_err, get_urls_form_html, format_and_filter_urls
from helper import S
from helper import Slave
import gevent
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class Spider(Slave):
    """
    slave抓取逻辑
    """

    def __init__(self, project_name):
        self.handle_method = None
        self.pre_url_queue = []
        self.http_helper = None
        self.current_url = ''  # 当前url
        self.pre_url_queue = []
        self.http_helper = helper.HttpHelper()
        Slave.__init__(self, project_name)

    def run(self, func, current_url, gevent_id):
        """
        :param func:
        :return:
        """
        self.handle_method = func

        # while True:
        # todo 需要些速度控制方法. gevent.sleep
        self.current_url = current_url

        print 'gevent_id: ' + str(gevent_id) + ' -- ' + self.project_name + ' -- ' + self.current_url
        if not self.current_url:
            # continue
            return
        self.put_data(urls_parsed=[self.current_url, ])
        crawl_result = self.http_helper.get(self.current_url)
        if not str(crawl_result[1]).startswith('20') \
                and not str(crawl_result[1]).startswith('30'):  # 如果不是200系列和300系列的状态码输出错误
            echo_err('gevent_id: ' + str(gevent_id) + ' -- ' + self.project_name +
                     ' -- URL: ' + self.current_url + ' 获取失败 HTTP code: ' + str(crawl_result[1]) + ' Runtime: ' + str(
                crawl_result[2]) + 'ms')
            # continue
            return

        # 如果抓取自定义函数存在dict返回值则将dict推送至服务器
        parse_result = self.handle_method(
            S(self, crawl_result[0], get_urls_form_html(self.current_url, crawl_result[0])))
        if not isinstance(parse_result, dict):
            # continue
            return

        if 'url' not in parse_result:
            parse_result['url'] = self.current_url
        if 'runtime' not in parse_result:
            parse_result['runtime'] = crawl_result[2]

        self.put_data(save=parse_result)

    def crawl(self, url=''):
        """
        仅加入远程待抓取队列
        self.run()会循环的从本地队列中获取url进行实际抓取
        :param string url:
        :return:
        """
        self.put_data(urls_add=(format_and_filter_urls(self.current_url, url),))

# from gevent import monkey
#
# monkey.patch_all()
# import gevent
#
#
# def start(project_name, callback):
# gevent.joinall([gevent.spawn(Spider(project_name).run, callback) for i in xrange(2)])
