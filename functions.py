#! coding=utf-8
import hashlib
import sys
import time
from mongo_single import Mongo


def get_project_list():
    """
    todo 测试是否支持中文
    :return:
    """
    get_project_list.cache = [v for v in Mongo.get().projects.find({}, {'_id': 0})]

    return get_project_list.cache


def md5(s):
    __md5 = hashlib.md5()
    __md5.update(str(s))
    return __md5.hexdigest()


def echo_err(msg):
    sys.stderr.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' ' + msg + '\r\n')