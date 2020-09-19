from flask import Blueprint, jsonify

from api_common import get_oems
from caching import cache

api = Blueprint('api_v2', __name__)


@api.route('/oems')
@cache.cached()
def api_v2_oems():
    oems = get_oems()
    response = {}

    for oem, devices_data in oems.items():
        print(oem, devices_data)
        response_devices_data = []

        for device_data in devices_data:
            response_devices_data.append({
                'model': device_data['model'],
                'name': device_data['name'],
            })

        response[oem] = response_devices_data

    return jsonify(response)
