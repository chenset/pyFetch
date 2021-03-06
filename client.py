#!/usr/bin/python
# coding=utf8
import click
import json
import traceback
from functions import echo_err
from helper import Socket_client
from spider import Spider
from gevent import monkey
import gevent

from helper import QueueSleepCtrl


def init():
    try:
        json_string = Socket_client.run(json.dumps({'init': 1}))
        return json.loads(json_string)
    except:
        return None


def run(gevent_id, project_name, source_code, init_url):
    run.restart = False
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
            # 项目有修改, 重新编码执行
            if spider.has_project_change():
                for item in load_projects():
                    if item['name'] == project_name:
                        spider = context_rebuild(item['name'], item['code'])

                        print 'gevent ID:' + str(gevent_id) + ' - project : ' + project_name + ' reload !!!!!!!!!!'
                        break

                continue

            response = spider.get_data()
            if not response:
                echo_err('gevent ID:' + str(gevent_id) + ' - project : ' + project_name + ' - 远程响应异常, 60秒后重试')
                gevent.sleep(60)
                continue

            # 准备重启
            if run.restart or ('restart' in response and response['restart']):
                run.restart = True
                echo_err('gevent ID:' + str(gevent_id) + ' - project : ' + project_name + ' - 准备重启中...')
                return  # 当该轮全部协程返回后, 调用处会再次重新开启新一轮. 以此达到重启的目的

            if 'urls' not in response or not response['urls']:
                echo_err('gevent ID:' + str(gevent_id) + ' - project : ' + project_name + ' - 无法从远程获取url队列, 10秒后重试' +
                         response['msg'] or '')
                gevent.sleep(10)
                continue

            spider.pre_url_queue += response['urls']

            # 执行爬取
            while spider.pre_url_queue:
                url = spider.pre_url_queue.pop(0)  # 出栈首位
                sleep = QueueSleepCtrl.get_sleep_times(url)
                # print sleep, ' -- gevent ID:' + str(gevent_id) + ' - project : ' + project_name + ' - ' + url
                gevent.sleep(sleep)
                spider.run(context['callback'], url, project_name, init_url, gevent_id)

    except:
        print traceback.format_exc()

    echo_err('gevent ID:' + str(gevent_id) + ' - project : ' + project_name + ' stop !!!!!!!!!!!!!!!')


def load_projects():
    res = init()
    while not res or 'projects' not in res or not res['projects']:
        res = init()
        msg = '. 无法连接远程服务器!'
        if res:
            msg = res.get('msg', '')
        echo_err(' 初始化失败, 10秒后重试' + msg)
        gevent.sleep(10)

    return res['projects']


@click.command()
@click.option('--host', '-h', default='127.0.0.1', type=str, help='pyFetch Service host.')
@click.option('--port', '-p', default=17265, type=int, help='pyFetch Service port.')
def cli(host, port):
    Socket_client.set_host(host)
    Socket_client.set_port(port)
    click.echo('Connecting %s:%s ...' % (host, port))

    monkey.patch_all()

    while True:
        joins = []
        gevent_id = 0  # 作为 gevent 的ID标识
        for project in load_projects():
            gevent_id += 1
            joins.append(gevent.spawn(run, gevent_id, project['name'], project['code'], project['init_url']))
            #
            # gevent_id += 1
            # joins.append(gevent.spawn(run, gevent_id, project['name'], project['code'], project['init_url']))

        gevent.joinall(joins)
        print click.echo('重启中......')


if __name__ == '__main__':
    cli()