#!/usr/bin/python
# coding=utf-8
import click
import zlib
import base64
import json
import traceback
from multiprocessing import Process, Manager
import gevent
from gevent import socket

from ser_handle import SerHandle
from web.web_ui import web_start
from helper import GlobalHelper, SlaveRecord
from slave_ctrl import SlaveCtrl
from functions import get_wan_ip


def request_handle(data, address):
    request = json.loads(data)

    slave_record.add_request_record(address[0])
    if 'urls_fail' in request and request['urls_fail']:
        slave_record.add_fails_record(address[0], request['urls_fail'])

    GlobalHelper.set('salve_record', slave_record.slave_record)

    restart_slave_list = GlobalHelper.get('restart_slave_list') or []
    if address[0] in restart_slave_list:
        # print restart_slave_list
        restart_slave_list.remove(address[0])
        GlobalHelper.set('restart_slave_list', restart_slave_list)
        # print restart_slave_list
        # print GlobalHelper.get('restart_slave_list')
        return json.dumps({'msg': '该客户端被手动重启中!', 'restart': 1})

    if slave_record.slave_record[address[0]]['static'] == '暂停中':
        return json.dumps({'msg': '. 该客户端被手动暂停中!'})

    if 'init' in request:
        projects = SlaveCtrl().code_ctrl()
        if not projects:
            return json.dumps({'msg': '. 暂无项目, 请访问WEB控制台添加项目!'})

        return json.dumps({'msg': '. 获取项目成功!', 'projects': projects})

    if 'project_name' not in request:
        return json.dumps({'msg': '未设置该项目名称'})

    handle = SerHandle(request['project_name'], request, address)

    if not handle.get_project():
        return json.dumps({'msg': '操作不存在的项目, 将该客户端重启!', 'restart': 1})

    if 'urls_parsed' in request and request['urls_parsed']:
        handle.urls_parsed()

    if 'urls_add' in request and request['urls_add'] and isinstance(request['urls_add'], list):
        handle.urls_add()

    if 'save' in request and request['save'] and isinstance(request['save'], list):
        handle.result_save()

    if handle.get_project() and handle.get_project()['static'] == '暂停中':
        return json.dumps({'msg': '. 该项目"' + request['project_name'] + '"被手动暂停中!'})

    response_url_list = []
    if 'get_urls' in request:
        response_url_list = handle.get_urls()

    msg = ''
    if not response_url_list:
        msg = ', 目前该项目已无可取的队列.'

    # 客户端会通过判断change_time的不同而reload项目
    return json.dumps({'msg': msg, 'urls': response_url_list,
                       'change_time': handle.get_project()['update_time']})


def socket_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(256)
    while True:
        client, address = sock.accept()
        gevent.spawn(socket_accept, client, address)


def socket_accept(sock, address):
    data = ''
    try:
        buff_size = 1024
        data = sock.recv(buff_size)
        data_len = int(data[0:10])
        while len(data) < data_len:
            data += sock.recv(buff_size)

        data = zlib.decompress(base64.b64decode(data[10:]))  # 解码解压
        send_date = str(request_handle(data, address))  # 内容处理函数
        send_date = base64.b64encode(zlib.compress(send_date))  # 压缩编码
        # send content前10个字符串用于标识内容长度.
        response_len = (str(len(send_date) + 10) + ' ' * 10)[0:10]
        sock.sendall(response_len + send_date)
        sock.shutdown(socket.SHUT_WR)
    except Exception, error:
        print traceback.format_exc()
        print error
        print address
        print data
    finally:

        sock.close()


@click.command()
@click.option('--host', '-h', default='0.0.0.0', type=str,
              help='pyFetch Service host and WEB service host. 0.0.0.0 is represent open to public network.')
@click.option('--port', '-p', default=17265, type=int, help='pyFetch Service port.')
@click.option('--wwwport', default=80, type=int, help='WEB Service port.')
def cli(host, port, wwwport):
    click.echo('\r\nService listening on %s:%s' % (host, port,))

    web_list = list()
    client_connect_list = list()
    web_list.append('local: http://127.0.0.1:%s' % wwwport)
    client_connect_list.append('local: python client.py --host 127.0.0.1 --port %s' % port)
    if host == '0.0.0.0':
        wan_ip = get_wan_ip()
        lan_ip = socket.gethostbyname(socket.gethostname())
        if lan_ip != wan_ip:
            web_list.append('lan  : http://%s:%s' % (lan_ip, wwwport))
            client_connect_list.append('lan  : python client.py --host %s --port %s' % (lan_ip, port))

        if wan_ip:
            web_list.append('wan  : http://%s:%s  PS: Maybe need to set up port forwarding' % (wan_ip, wwwport))
            client_connect_list.append(
                'wan  : python client.py --host %s --port %s  PS: Maybe need to set up port forwarding' %
                (wan_ip, port))

    click.echo('\r\nAccess console via:')
    for item in web_list:
        click.echo(item)

    click.echo('\r\nClient connection use:')
    for item in client_connect_list:
        click.echo(item)

    click.echo('\r\nListening ...')

    global_process_var = Manager().dict()
    GlobalHelper.init(global_process_var)

    web_ui = Process(target=web_start, args=(global_process_var, host, wwwport))
    web_ui.start()

    global slave_record
    slave_record = SlaveRecord.get_instance()
    GlobalHelper.set('salve_record', slave_record.slave_record)

    socket_server(host, port)
    web_ui.join()


if __name__ == '__main__':
    cli()




