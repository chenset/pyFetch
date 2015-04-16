from flask import Flask, url_for, redirect, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
    # return url_for('static', filename='css/base.css')
    # return url_for('static', filename='js/base.js')

#
# with app.test_request_context():
# print url_for('index')
# print url_for('login')
#     print url_for('login', next='/')
#     print url_for('profile', username='John Doe')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)