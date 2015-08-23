# coding=utf8
import json
import time
import traceback
from functions import socket_client, echo_err
from spider import Spider
from gevent import monkey

monkey.patch_all()
import gevent


def init():
    try:
        json_string = socket_client(json.dumps({'init': 1}))
        return json.loads(json_string)
    except:
        return None


def run(gID, project_name, source_code):
    context = {}

    def start(callback):
        context['callback'] = callback

    def context_rebuild(new_name, new_code):
        code = compile(new_code, 'test_mode_file', 'exec')
        exec code in {'start': start}
        return Spider(new_name)

    try:
        spider = context_rebuild(project_name, source_code)

        while True:
            if spider.has_project_change():
                for item in load_projects():
                    if item['name'] == project_name:
                        spider = context_rebuild(item['name'], item['code'])

                        print 'gevent ID:' + str(gID) + ' -- project : ' + project_name + ' reload !!!!!!!!!!'
                        break

                continue

            response = spider.get_data()
            if not response:
                echo_err('远程响应异常, 60秒后重试')
                gevent.sleep(60)
                continue

            if 'urls' not in response or not response['urls']:
                echo_err('无法从远程获取url队列, 10秒后重试 ' + response['msg'] or '')
                gevent.sleep(10)
                continue

            spider.pre_url_queue += response['urls']

            while spider.pre_url_queue:
                url = spider.pre_url_queue.pop(0)  # 出栈首位
                spider.run(context['callback'], url, gID)

    except Exception, e:
        print traceback.format_exc()

    echo_err('gevent ID:' + str(gID) + ' -- project : ' + project_name + ' stop !!!!!!!!!!!!!!!')


def load_projects():
    res = init()
    while not res or 'projects' not in res or not res['projects']:
        res = init()
        echo_err('无法连接远程服务器, 初始化失败, 10秒后重试!')
        time.sleep(10)

    return res['projects']


if __name__ == '__main__':
    joins = []
    gID = 0  # 作为 gevent 的ID标识
    for project in load_projects():
        print project
        gID += 1
        joins.append(gevent.spawn(run, gID, project['name'], project['code']))

        gID += 1
        joins.append(gevent.spawn(run, gID, project['name'], project['code']))

    gevent.joinall(joins)