# coding=utf-8
import helper
from functions import echo_err, get_urls_form_html


class SpiderForTest():
    http_helper = None
    current_url = ''
    handle_method = None

    def __init__(self):
        self.http_helper = helper.HttpHelper()

    def run(self, func):
        res = {}
        self.handle_method = func

        crawl_result = self.http_helper.get(self.current_url)
        if crawl_result[1] not in (200, 201):
            return {
                'error': 'URL: ' + self.current_url + ' 获取失败 HTTP code: ' + str(crawl_result[1]) + ' Runtime: ' + str(
                    crawl_result[2]) + 'ms'}

        urls = get_urls_form_html(self.current_url, crawl_result[0])
        res['urls'] = list(set(urls))
        res['html'] = crawl_result[0]  # todo 如果返回html可能占用带宽过大.
        res['http_code'] = crawl_result[1]

        # 如果抓取自定义函数存在dict返回值则将dict推送至服务器
        parse_result = self.handle_method(
            helper.S(self, crawl_result[0], urls))

        if not isinstance(parse_result, dict):
            return res

        if 'url' not in parse_result:
            parse_result['url'] = self.current_url
        if 'runtime' not in parse_result:
            parse_result['runtime'] = crawl_result[2]

        res['result'] = parse_result

        return res

    def crawl(self, url=''):
        self.current_url = url


def test_run(form_data):
    context = {}

    def start(project_name, callback):
        context['project_name'] = project_name
        context['callback'] = callback

    code = compile(form_data['code'], 'test_model_file', 'exec')
    exec code in {'start': start}
    spider = SpiderForTest()
    spider.crawl(form_data['init_url'])
    return spider.run(context['callback'])
