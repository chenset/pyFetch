#!coding=utf8
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


def run(project_name, source_code):
    context = {}

    def start(callback):
        context['callback'] = callback

    try:
        code = compile(source_code, 'test_mode_file', 'exec')
        exec code in {'start': start}
        spider = Spider(project_name)
        spider.run(context['callback'])
    except Exception, e:
        print traceback.format_exc()


if __name__ == '__main__':
    res = init()
    while not res or 'projects' not in res or not res['projects']:
        res = init()
        echo_err('无法初始化,10秒后重试')
        time.sleep(10)

    joins = []
    for project in res['projects']:
        print project
        joins.append(gevent.spawn(run, project['name'], project['code']))
        joins.append(gevent.spawn(run, project['name'], project['code']))

    gevent.joinall(joins)