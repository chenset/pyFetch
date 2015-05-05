from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from mongo_single import Mongo

app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY='development key',
))


@app.route('/')
def index():
    # response = 'queue len: ' + str(Mongo.get()['queue'].count()) + '<br/>'
    # response += 'parsed len: ' + str(Mongo.get()['parsed'].count()) + '<br/>'
    # response += 'result len: ' + str(Mongo.get()['result'].count()) + '<br/>'
    return render_template('index.html', )


@app.route('/<dir>/<action>')
def project(dir, action):
    return render_template(dir + '.html')


def web_start():
    app.run('0.0.0.0', 80, debug=True)


if __name__ == '__main__':
    web_start()