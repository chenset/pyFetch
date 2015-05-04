from flask import Flask
from mongo_single import Mongo

app = Flask(__name__)


@app.route('/')
def hello_world():
    response = 'queue len: ' + str(Mongo.get()['queue'].count()) + '<br/>'
    response += 'parsed len: ' + str(Mongo.get()['parsed'].count()) + '<br/>'
    response += 'result len: ' + str(Mongo.get()['result'].count()) + '<br/>'
    return '<h3>Hello pySpiders!</h3><br/>' + response


def web_start():
    app.run('0.0.0.0', 80, debug=False)