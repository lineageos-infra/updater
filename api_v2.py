from flask import Blueprint, jsonify, request

from api_common import get_oems, get_device_builds, get_device_data, get_device_versions
from caching import cache
from changelog import GerritServer, get_changes
from config import Config

api = Blueprint('api_v2', __name__)

gerrit = GerritServer(Config.GERRIT_URL)


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
@cache.cached()
def api_v2_device_builds(device):
    device_data = get_device_data(device)
    builds = get_device_builds(device)

    return jsonify({
        'name': device_data['name'],
        'model': device_data['model'],
        'oem': device_data['oem'],
        'builds': builds,
    })


@api.route('/changes')
@cache.cached()
def api_v2_changes():
    args = request.args.to_dict(False)
    device = args.get('device', None, str)
    before = args.get('before', -1, int)

    versions = request.args.get('version')
    if not versions:
        versions = get_device_versions(device)
    elif type(versions) != list:
        if type(versions) != str:
            raise ValueError('Version is not a string')

        versions = [versions]

    return jsonify(get_changes(gerrit, device, before, versions, Config.STATUS_URL))
