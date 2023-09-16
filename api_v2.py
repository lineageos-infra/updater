from flask import Blueprint, jsonify, request

from api_common import get_oems, get_device_builds, get_device_data, get_device_versions
from changelog import GerritServer, get_project_repo, get_paginated_changes, get_timestamp, get_device_dependencies, get_type
from config import Config
from custom_exceptions import InvalidValueException, UpstreamApiException, DeviceNotFoundException

import extensions

api = Blueprint('api_v2', __name__)
gerrit = GerritServer(Config.GERRIT_URL)


@api.route('/oems')
@extensions.cache.cached()
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
@extensions.cache.cached()
def api_v2_device(device):
    device_data = get_device_data(device)

    return jsonify({
        'name': device_data['name'],
        'model': device_data['model'],
        'oem': device_data['oem'],
        'info_url': Config.WIKI_INFO_URL.format(device=device),
        'versions': get_device_versions(device),
        'dependencies': get_device_dependencies(device),
    })


@api.route('/devices/<string:device>/builds')
@extensions.cache.cached()
def api_v2_device_builds(device):
    builds = get_device_builds(device)

    def get_download_url(file):
        return Config.DOWNLOAD_BASE_URL + file['filepath']

    for build in builds:
        for file in build['files']:
            file['url'] = get_download_url(file)

        build['files'][0]['date'] = build['date']
        build['files'][0]['datetime'] = build['datetime']
        build['files'][0]['type'] = build['type']

    return jsonify(builds)


@api.route('/changes')
@extensions.cache.cached(query_string=True)
def api_v2_changes():
    page = request.args.get('page', default=0, type=int)
    changes = get_paginated_changes(gerrit, page=page)
    response = []

    for change in changes:
        response.append({
            'url': change.url,
            'project': change.project,
            'repository': get_project_repo(change.project),
            'branch': change.branch,
            'subject': change.subject,
            'submitted': get_timestamp(change.submitted),
            'updated': get_timestamp(change.updated),
            'type': get_type(change.project),
        })

    return jsonify(response)


@api.errorhandler(DeviceNotFoundException)
@api.errorhandler(InvalidValueException)
@api.errorhandler(UpstreamApiException)
@api.errorhandler(UpstreamApiException)
def api_v2_handle_exception(e):
    return jsonify({
        'error': e.message
    }), 400


@api.errorhandler(ConnectionError)
def api_v2_handle_connection_failed_exception(e):
    return jsonify({
        'error': 'Connection failed'
    }), 400
