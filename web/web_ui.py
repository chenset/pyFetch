#! coding=utf8
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify, json
from mongo_single import Mongo
import time
import os
from functions import get_project_name_list
from helper import GlobalHelper

# from gevent import monkey
# monkey.patch_socket()  # fixme patch_all 会影响跨进程通讯或者异步抓取 1/2

from gevent.wsgi import WSGIServer
from flask.ext.compress import Compress

app = Flask(__name__)
Compress(app)

app.config.update(dict(
    SECRET_KEY='development key',
))


def get_template(template_path):
    with open(os.path.dirname(os.path.abspath(__file__)) + '/templates/' + template_path) as f:
        return f.read()


@app.errorhandler(404)
def page_not_found(error):
    return redirect('/project')


@app.route('/')
def index():
    return redirect('/main.html')


@app.route('/<path>')
@app.route('/project/<path>')
@app.route('/project/task/<path>')
@app.route('/project/edit/<path>')
@app.route('/project/add/<path>')
@app.route('/slave/task/<path>')
@app.route('/slave/result/<path>')
@app.route('/project/result/<path>')
def default(path):
    """
    首次全新请求(即不经过angular的请求)url地址的route规则
    """
    return get_template('main.html')


@app.route('/component/<page>')
@app.route('/component/task/<page>')
def page(page):
    return get_template('component/' + page + '.html')


@app.route('/api/test')
def api_test():
    print GlobalHelper.get('salve_record')
    # time.sleep(10)
    return jsonify({'fd': 1})


@app.route('/api/slave')
def api_slave():
    return jsonify(GlobalHelper.get('salve_record') or {})


@app.route('/api/project')
def get_projects():
    project_dict = {}
    for project_name in get_project_name_list():
        project_dict[project_name] = {'name': project_name}

    return jsonify(project_dict)


@app.route('/api/slave/<ip>')
def get_slave_tasks(ip):
    res = []
    for project_name in get_project_name_list():
        for doc in Mongo.get()['parsed_' + project_name].find({'slave_ip': ip}).sort('_id', -1).limit(100):
            del doc['_id']
            res.append(doc)
    return json.dumps(res)


@app.route('/api/task/<project_name>')
def get_project_tasks(project_name):
    res = []
    for doc in Mongo.get()['parsed_' + project_name].find().sort('_id', -1).limit(100):
        del doc['_id']
        res.append(doc)
    return json.dumps(res)


@app.route('/api/result/<project_name>')
def get_results(project_name):
    res = []
    for doc in Mongo.get()['result_' + project_name].find().sort('_id', -1).limit(100):
        del doc['_id']
        res.append(doc)
    return json.dumps(res)


def web_start(dd):
    """
    当service.py为入口时会调用这里
    """
    GlobalHelper.init(dd)
    http_server = WSGIServer(('0.0.0.0', 80), app)
    http_server.serve_forever()


if __name__ == '__main__':
    """
    当前文件为入口时会调用这里
    """
    app.run('0.0.0.0', 80, debug=True, threaded=True)