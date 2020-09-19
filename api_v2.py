from flask import Blueprint, jsonify

from api_common import get_oems, get_device_builds, get_device_data
from caching import cache

api = Blueprint('api_v2', __name__)


@api.route('/oems')
@cache.cached()
def api_v2_oems():
    oems = get_oems()
    response = []

    for oem, devices_data in oems.items():
        response_oem = {
            'name': oem,
            'devices': []
        }

        for device_data in devices_data:
            response_oem['devices'].append({
                'model': device_data['model'],
                'name': device_data['name'],
            })

        response.append(response_oem)

    return jsonify(response)


@api.route('/devices/<string:device>')
def api_v2_device_builds(device):
    device_data = get_device_data(device)
    builds = get_device_builds(device)

    return jsonify({
        'name': device_data['name'],
        'model': device_data['model'],
        'oem': device_data['oem'],
        'builds': builds,
    })
