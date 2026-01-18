"""routes.py"""
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello world!!!'


@app.route('/items')
def get_items():
    items = {
        'id': 1,
        'username': 'Luka'
    }
    return items


if __name__ == '__main__':
    app.run(debug=True)
