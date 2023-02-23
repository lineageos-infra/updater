import flask
from flask_caching import Cache
from flask_cors import CORS

cache = Cache()
cors = CORS()

def setup(app: flask.Flask) -> None:
    cache.init_app(app)
    cors.init_app(app)