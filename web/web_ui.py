#! coding=utf8
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify, json
from mongo_single import Mongo
import time
from functions import get_project_name_list

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY='development key',
))


def get_template(template_path):
    with open('templates/' + template_path) as f:
        return f.read()


@app.errorhandler(404)
def page_not_found(error):
    return redirect('/')


@app.route('/')
def index():
    return get_template('main.html')


@app.route('/<path>')
@app.route('/project/<path>')
@app.route('/project/task/<path>')
@app.route('/slave/task/<path>')
@app.route('/slave/result/<path>')
@app.route('/project/result/<path>')
def one(path):
    """
    首次全新请求(即不经过angular的请求)url地址的route规则
    """
    return get_template('main.html')


@app.route('/component/<page>')
@app.route('/component/task/<page>')
def two(page):
    return get_template('component/' + page + '.html')


@app.route('/api/test')
def api_test():
    time.sleep(0.1)
    return jsonify({'fd': 1})


@app.route('/api/project')
def get_projects():
    project_dict = {}
    for project_name in get_project_name_list():
        project_dict[project_name] = {'name': project_name}

    return jsonify(project_dict)


@app.route('/api/task/<project_name>')
def get_tasks(project_name):
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


def web_start():
    app.run('0.0.0.0', 80, debug=True)


if __name__ == '__main__':
    web_start()