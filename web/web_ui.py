#! coding=utf8
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from mongo_single import Mongo
import time

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
    return '{}'


def web_start():
    app.run('0.0.0.0', 80, debug=True)


if __name__ == '__main__':
    web_start()