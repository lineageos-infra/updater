from flask import Blueprint, jsonify

from api_common import get_oems
from caching import cache

api = Blueprint('api_v2', __name__)


@api.route('/oems')
@cache.cached()
def api_v1_devices():
    return jsonify(get_oems())
