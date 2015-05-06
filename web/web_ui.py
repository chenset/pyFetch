from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from mongo_single import Mongo

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
def one(path):
    return get_template(path + '.html')


@app.route('/<path>/<param>')
def two(path, param):
    return get_template('main.html')


def web_start():
    app.run('0.0.0.0', 80, debug=True)


if __name__ == '__main__':
    web_start()