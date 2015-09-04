#! coding=utf8
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify, json
from mongo_single import Mongo
import time
import os
import traceback
from functions import get_project_list, md5
from helper import GlobalHelper
from spider_for_test import test_run
from bson import ObjectId

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
    with open(os.path.dirname(os.path.abspath(__file__)) + '/templates/' + template_path) as f:  # todo 后期上缓存
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
    try:
        new_records = {}
        salve_records = GlobalHelper.get('salve_record')

        if not salve_records:
            return jsonify(new_records)

        for (key, value) in salve_records.items():
            item = dict(value)

            ip_fragment = key.split('.')
            ip_fragment[1] = ip_fragment[1].zfill(3)
            ip_fragment[2] = ip_fragment[2].zfill(3)
            ip_fragment[1] = ip_fragment[1][0:2] + '*'
            # ip_fragment[2] = '**' + ip_fragment[2][2:]
            ip_fragment[2] = '***'
            item['ip'] = '.'.join(ip_fragment)

            new_records[value['_id']] = item

        return jsonify(new_records)
    except:
        print traceback.format_exc()


@app.route('/api/slave/<slave_id>')
def get_slave_tasks(slave_id):
    res = []
    try:
        slave_record = Mongo.get()['slave_record'].find_one({'_id': ObjectId(slave_id)})
        if not slave_record:
            raise Exception('不存在的记录!')
    except:
        return json.dumps(res)

    for project in get_project_list():
        for doc in Mongo.get()['parsed_' + project['name']].find({'slave_ip': slave_record['ip']}).sort('_id',
                                                                                                        -1).limit(100):
            del doc['_id']
            res.append(doc)
    print res
    return json.dumps(res)


@app.route('/api/slave/<slave_id>/restart')
def restart_slave(slave_id):
    try:
        slave_record = Mongo.get()['slave_record'].find_one({'_id': ObjectId(slave_id)})
        if not slave_record:
            raise Exception('不存在的记录!')
    except:
        return jsonify({'success': False, 'msg': '不存在的记录!'})

    restart_slave_list = GlobalHelper.get('restart_slave_list') or []
    restart_slave_list.append(slave_record['ip'])

    GlobalHelper.set('restart_slave_list', list(set(restart_slave_list)))
    return jsonify({'success': True, 'msg': '重启中!'})


@app.route('/api/slave/<slave_id>/toggle')
def toggle_slave(slave_id):
    try:
        slave_record = Mongo.get()['slave_record'].find_one({'_id': ObjectId(slave_id)})
        if not slave_record:
            raise Exception('不存在的记录!')
    except:
        return jsonify({'success': False, 'msg': '不存在的记录!'})

    slave_record['data']['static'] = '抓取中' if slave_record['data']['static'] == '暂停中' else '暂停中'
    try:
        Mongo.get()['slave_record'].update({'_id': ObjectId(slave_id)},
                                           {'$set': {'data.static': slave_record['data']['static']}})
        global_salve_record = GlobalHelper.get('salve_record')
        global_salve_record[slave_record['ip']]['static'] = slave_record['data']['static']
        GlobalHelper.set('salve_record', global_salve_record)
    except:
        print traceback.format_exc()
    return jsonify({'success': True, 'msg': '切换成功!'})


@app.route('/api/project/<project_id>/toggle')
def toggle_project(project_id):
    try:
        project = Mongo.get()['projects'].find_one({'_id': ObjectId(project_id)})
        if not project:
            raise Exception('不存在的记录!')
    except:
        return jsonify({'success': False, 'msg': '不存在的记录!'})

    project['static'] = '抓取中' if project['static'] == '暂停中' else '暂停中'

    Mongo.get()['projects'].update({'_id': ObjectId(project_id)},
                                   {'$set': {'static': project['static']}})
    return jsonify({'success': True, 'msg': '切换成功!'})


@app.route('/api/project')
def get_projects():
    project_dict = {}
    for project in get_project_list():
        project_dict[project['name']] = {
            '_id': str(project['_id']),
            'name': project['name'],
            'static': project['static'],
            'queue_len': Mongo.get()['queue_' + project['name']].count(),
            'parsed_len': Mongo.get()['parsed_' + project['name']].count(),
            'result_len': Mongo.get()['result_' + project['name']].count(),
        }

    return jsonify(project_dict)


@app.route('/api/project/<name>')
def get_project_by_name(name):
    res = list(Mongo.get().projects.find({'name': name}, {'_id': 0}))
    if not res:
        return jsonify({})
    return jsonify(res[0])


@app.route('/api/project/save', methods=['POST'])
def save_project():
    form_data = json.loads(request.data)  # todo 需要验证表单数据

    exists_project = list(Mongo.get()['projects'].find({'name': form_data['name']}, {'_id': 1, 'add_time': 1}).limit(1))

    if 'edit' not in form_data and exists_project:
        return jsonify({'success': False, 'msg': '计划名称已经存在!'})

    # 新增计划或更新计划
    data = {
        'name': form_data['name'],
        'init_url': form_data['init_url'],
        'desc': form_data['desc'] if 'desc' in form_data else '',
        'code': form_data['code'],
        'static': '暂停中',
        'update_time': int(time.time()),
        'add_time': exists_project[0]['add_time'] if exists_project else int(time.time()),
    }
    Mongo.get()['projects'].update({'name': form_data['name']}, data, True)

    # 当是新计划时的初始化
    if 'edit' not in form_data:
        Mongo.get()['queue_' + form_data['name']].insert(
            {
                'url': form_data['init_url'],
                'url_md5': md5(form_data['init_url']),
                'flag_time': 0,
                'add_time': int(time.time()),
                'slave_ip': '0.0.0.0'
            })

        # 在没创建集合前设置索引mongodb会自动创建该集合并赋索引
        Mongo.get()['parsed_' + form_data['name']].ensure_index('url_md5', unique=True)
        Mongo.get()['queue_' + form_data['name']].ensure_index('url_md5', unique=True)

        # 有新计划加入, 重启全部slave
        restart_slave_list = GlobalHelper.get('restart_slave_list') or []
        for slave_record in Mongo.get()['slave_record'].find():
            restart_slave_list.append(slave_record['ip'])
        GlobalHelper.set('restart_slave_list', list(set(restart_slave_list)))

    return jsonify({'success': True, 'msg': '保存成功!'})


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


@app.route('/api/project/exec_test', methods=['POST'])
def exec_test():
    form_data = json.loads(request.data)  # todo 需要验证表单数据

    result = test_run(form_data)
    if 'error' in result:
        return json.dumps({'success': False, 'msg': result['error'], 'result': {'stdout': result['stdout']}})

    result['urls'] = result['urls'][::-1]

    return json.dumps({'success': True, 'msg': '成功', 'result': result})


def web_start(dd, host, web_port):
    """
    当service.py为入口时会调用这里
    """
    GlobalHelper.init(dd)

    http_server = WSGIServer((host, web_port), app)
    http_server.serve_forever()


if __name__ == '__main__':
    """
    当前文件为入口时会调用这里
    """
    app.run('0.0.0.0', 80, debug=True, threaded=True)