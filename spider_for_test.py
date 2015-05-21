# coding=utf-8
import helper
import traceback
from functions import get_urls_form_html, stdoutIO


class SpiderForTest():
    http_helper = None
    current_url = ''
    handle_method = None
    rest_result = {}

    def __init__(self):
        self.rest_result = {'urls': [], 'current_url': '', 'http_code': 0, 'result': {}}
        self.http_helper = helper.HttpHelper()

    def run(self, func):
        self.handle_method = func

        crawl_result = self.http_helper.get(self.current_url)
        if not str(crawl_result[1]).startswith('20') \
                and not str(crawl_result[1]).startswith('30'):  # 如果不是200系列和300系列的状态码输出错误
            return {
                'error': 'URL: ' + self.current_url + ' 获取失败 HTTP code: ' + str(crawl_result[1]) + ' Runtime: ' + str(
                    crawl_result[2]) + 'ms'}

        urls = get_urls_form_html(self.current_url, crawl_result[0])
        self.rest_result['current_url'] = self.current_url
        self.rest_result['http_code'] = crawl_result[1]

        # 如果抓取自定义函数存在dict返回值则将dict推送至服务器
        parse_result = self.handle_method(
            helper.S(self, crawl_result[0], urls))

        if not isinstance(parse_result, dict):
            return self.rest_result

        if 'url' not in parse_result:
            parse_result['url'] = self.current_url
        if 'runtime' not in parse_result:
            parse_result['runtime'] = crawl_result[2]

        self.rest_result['result'] = parse_result

        return self.rest_result

    def crawl(self, url='', add_urls_flag=True):
        self.current_url = url
        if add_urls_flag:
            url not in self.rest_result['urls'] and self.rest_result['urls'].append(url)


def test_run(form_data):
    context = {}

    def start(callback):
        context['callback'] = callback

    result = {
        'urls': [], 'current_url': '', 'http_code': 0, 'result': {}, 'stdout': ''
    }
    with stdoutIO() as s:
        try:
            code = compile(form_data['code'], 'test_mode_file', 'exec')
            exec code in {'start': start}
            spider = SpiderForTest()
            spider.crawl(form_data['init_url'], False)
            result = spider.run(context['callback'])
        except Exception, e:
            print traceback.format_exc()

    result['stdout'] = s.getvalue().strip()
    return result
