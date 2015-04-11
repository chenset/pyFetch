#!/usr/local/python2.7/bin/python
#coding=utf8

import socket
import sys
import select
import errno
import json
import time
import traceback
import fun


class SocketServer:
    monitors = []
    password = 'fgdgd_fdsf_fdsf.gfd'
    username = 'dsfsdfsdf'
    end_with = 'end[\ddd*&^@#$'

    def __init__(self):
        pass

    def attach(self, monitor):
        if monitor not in self.monitors:
            self.monitors.append(monitor)

    def shutdown(self, data):
        """
        程序结束指令, 一些保存清理操作
        """
        fun.queue_save()  # 将redis的内存数据写入硬盘

        fun.info()  # 输出仓库数据

        sys.exit(0)  # 退出程序

    def execute(self, data):
        if data['method'] == 'get':
            fun.random_info()  # 随机概率生成统计数据
            return fun.get()
        elif data['method'] == 'put':
            return fun.put(data)
        elif data['method'] == 'get_patterns':
            return fun.get_patterns()
        elif data['method'] == 'shutdown':
            self.shutdown(data)

        # 默认禁止访问
        return {'msg': 'deny execute ,command ' + data['method'] + ' do not allow', 'success': False}

    def verify(self, username, password):
        if username == self.username and password == self.password:  # 暂时支持单用户
            return True
        else:
            return False

    def listen(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        except socket.error, msg:
            print 'error whit code 1 :' + str(msg)
            sys.exit()

        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error, msg:
            print 'error whit code 2'
            sys.exit()

        try:
            sock.bind(('', 9999))
        except socket.error, msg:
            print 'error whit code 3'
            sys.exit()

        try:
            sock.listen(10)
        except socket.error, msg:
            print 'error whit code 1'
            sys.exit()

        try:
            se_epoll = select.epoll()
            se_epoll.register(sock.fileno(), select.EPOLLIN)
        except select.error, msg:
            print 'error whit code 5'
            sys.exit()

        connections = {}
        addresses = {}
        datalist = {}
        parse_start_time = 0  # 初始化
        while True:
            epoll_list = se_epoll.poll()
            for fd, events in epoll_list:
                if fd == sock.fileno():
                    conn, addr = sock.accept()
                    conn.setblocking(0)
                    se_epoll.register(conn.fileno(), select.EPOLLIN | select.EPOLLET)
                    connections[conn.fileno()] = conn
                    addresses[conn.fileno()] = addr
                    connect_start_time = time.time()  # 開始連接的時間
                elif select.EPOLLIN & events:
                    parse_start_time = time.time()
                    datas = ''
                    count_empty_datas = 0  # 空数据会在客户端不等待接收返回值的情况发生
                    while True:
                        try:
                            data = connections[fd].recv(1024)
                            if not data:
                                count_empty_datas += 1  # 累加空数据次数
                                if not datas or count_empty_datas > 1:  # 如果空数据次数超过1次退出线程
                                    se_epoll.unregister(fd)
                                    connections[fd].close()
                                    break
                            else:
                                datas += data

                        except socket.error, msg:
                            if msg.errno == errno.EAGAIN:
                                if datas.endswith(self.end_with):
                                    datalist[fd] = datas.rstrip(self.end_with)
                                    se_epoll.modify(fd, select.EPOLLET | select.EPOLLOUT)
                                    break
                            else:
                                se_epoll.unregister(fd)
                                connections[fd].close()

                                break

                elif select.EPOLLHUP & events:
                    se_epoll.unregister(fd)
                    connections[fd].close()
                elif select.EPOLLOUT & events:
                    try:
                        data = json.loads(datalist[fd])
                    except:
                        print ' ------------------------------------------------------------------------------- ------------------------------------------------------------------------------- -------------------------------------------------------------------------------'
                        traceback.print_exc()
                        print datalist[fd]
                        print ' ------------------------------------------------------------------------------- ------------------------------------------------------------------------------- -------------------------------------------------------------------------------'
                        data = None

                    # print data
                    #必须是字典 , 密码必须正确
                    if isinstance(data, dict) and self.verify(data['username'], data['password']):
                        result = self.execute(data['function'])
                    else:
                        result = {'msg': 'Deny access', 'success': False}

                    result['current_cmd_execute_time'] = round((time.time() - parse_start_time) * 1000, 2)
                    result = json.dumps(result)

                    send_len = 0
                    try:
                        while True:
                            send_len += connections[fd].send(result[send_len:])
                            if send_len == len(result):
                                break
                        se_epoll.modify(fd, select.EPOLLIN | select.EPOLLET)
                    except:
                        continue
                else:
                    continue