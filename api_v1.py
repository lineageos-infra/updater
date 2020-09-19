from flask import Blueprint, jsonify, request

from api_common import get_builds, get_device_version, get_build_types, get_device_builds
from caching import cache
from changelog.gerrit import GerritServer, GerritJSONEncoder
from changelog import get_changes
from config import Config

api = Blueprint('api_v1', __name__)
api.json_encoder = GerritJSONEncoder

gerrit = GerritServer(Config.GERRIT_URL)


@api.route('/<string:device>/<string:romtype>/<string:incrementalversion>')
def api_v1_index(device, romtype, incrementalversion):
    after = request.args.get('after')
    version = request.args.get('version')

    return get_build_types(device, romtype, after, version)


@api.route('/types/<string:device>/')
@cache.cached()
def api_v1_get_types(device):
    data = get_device_builds(device)
    types = {'nightly'}
    for build in data:
        types.add(build['type'])
    return jsonify({'response': list(types)})


@api.route('/changes/<device>/')
@api.route('/changes/<device>/<int:before>/')
@api.route('/changes/<device>/-1/')
@cache.cached()
def api_v1_changes(device='all', before=-1):
    version = get_device_version(device)
    if version:
        versions = [version]
    else:
        versions = []

    changes, last = get_changes(gerrit, device, before, versions)

    return jsonify({
        'last': last,
        'res': changes,
    })


@api.route('/devices')
@cache.cached()
def api_v1_devices():
    data = get_builds()
    versions = {}
    for device in data.keys():
        for build in data[device]:
            versions.setdefault(build['version'], set()).add(device)

    for version in versions.keys():
        versions[version] = list(versions[version])
    return jsonify(versions)
