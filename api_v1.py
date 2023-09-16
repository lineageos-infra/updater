from flask import Blueprint, jsonify, request

from api_common import get_builds, get_device_version, get_build_types, get_device_builds
from changelog.gerrit import GerritServer
from changelog import get_changes, get_timestamp
from config import Config

import extensions

api = Blueprint('api_v1', __name__)

gerrit = GerritServer(Config.GERRIT_URL)


@api.route('/<string:device>/<string:romtype>/<string:incrementalversion>')
def api_v1_index(device, romtype, incrementalversion):
    after = request.args.get('after')
    version = request.args.get('version')

    return get_build_types(device, romtype, after, version)


@api.route('/types/<string:device>/')
@extensions.cache.cached()
def api_v1_get_types(device):
    data = get_device_builds(device)
    types = {'nightly'}
    for build in data:
        types.add(build['type'])
    return jsonify({'response': list(types)})


@api.route('/changes/<device>/')
@api.route('/changes/<device>/<int:before>/')
@api.route('/changes/<device>/-1/')
@extensions.cache.cached()
def api_v1_changes(device='all', before=-1):
    version = get_device_version(device)
    if version:
        if float(version) >= 20:
            versions = [version, version.split('.')[0]]
        else:
            versions = [version]
    else:
        versions = []

    response_changes = []
    try:
        changes, last = get_changes(gerrit, device, before, versions)
        for change in changes:
            response_changes.append({
                'project': change.project,
                'subject': change.subject,
                'submitted': get_timestamp(change.submitted),
                'updated': get_timestamp(change.updated),
                'url': change.url,
                'owner': change.owner,
                'labels': change.labels
            })
    except ConnectionError:
        last = 0
        response_changes.append({
            'project': None,
            'subject': None,
            'submitted': 0,
            'updated': 0,
            'url': Config.STATUS_URL,
            'owner': None,
            'labels': None
        })

    return jsonify({
        'last': last,
        'res': response_changes,
    })


@api.route('/devices')
@extensions.cache.cached()
def api_v1_devices():
    data = get_builds()
    versions = {}
    for device in data.keys():
        for build in data[device]:
            versions.setdefault(build['version'], set()).add(device)

    for version in versions.keys():
        versions[version] = list(versions[version])
    return jsonify(versions)
