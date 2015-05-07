#! coding=utf-8
import hashlib
import sys
import time
from mongo_single import Mongo


def get_project_name_list():
    """

    todo 测试是否支持中文
    :return:
    """
    project_name_list = []
    for collection in Mongo.get().collection_names():
        if collection == 'system.indexes':
            continue

        project_name = ''
        if collection.startswith('parsed_'):
            project_name = collection.replace('parsed_', '')
        elif collection.startswith('queue_'):
            project_name = collection.replace('queue_', '')
        elif collection.startswith('result_'):
            project_name = collection.replace('result_', '')
        if project_name and project_name not in project_name_list:
            project_name_list.append(project_name)

    return project_name_list


def md5(s):
    __md5 = hashlib.md5()
    __md5.update(str(s))
    return __md5.hexdigest()


def echo_err(msg):
    sys.stderr.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' ' + msg + '\r\n')