from flask import Flask
from flask.ext.cache import Cache

app = Flask(__name__)
cache = Cache(app)


def make_response():
    response = 'Hello Python!\n'
    return response


@app.route('/')
def index():
    return make_response()


@app.route('/cached/')
@cache.cached()
def cached_index():
    return make_response()
