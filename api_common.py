import json
import os

import arrow
import requests

from flask import jsonify
from caching import cache
from config import Config
from custom_exceptions import UpstreamApiException, DeviceNotFoundException


@cache.memoize()
def get_builds():
    try:
        req = requests.get(Config.UPSTREAM_URL)
        if req.status_code != 200:
            raise UpstreamApiException('Unable to contact upstream API')
        return json.loads(req.text)
    except Exception as e:
        print(e)
        raise UpstreamApiException('Unable to contact upstream API')


def get_devices_with_builds():
    return get_builds().keys()


def get_device_builds(device):
    builds = get_builds()
    if device not in builds:
        raise DeviceNotFoundException('This device has no available builds. Please select another device.')
    return builds[device]


@cache.memoize()
def get_devices_data():
    devices_data = []

    if os.path.isfile(Config.DEVICES_JSON_PATH):
        with open(Config.DEVICES_JSON_PATH) as f:
            devices_data += json.loads(f.read())
    else:
        devices_data += requests.get(Config.OFFICIAL_DEVICES_JSON_URL).json()

    if os.path.isfile(Config.DEVICES_LOCAL_JSON_PATH):
        with open(Config.DEVICES_LOCAL_JSON_PATH) as f:
            devices_data += json.loads(f.read())

    devices_data_with_builds = []
    devices_with_builds = get_devices_with_builds()
    for device_data in devices_data:
        if device_data['model'] in devices_with_builds:
            devices_data_with_builds.append(device_data)

    return devices_data_with_builds


@cache.memoize()
def get_device_data(device):
    devices_data = get_devices_data()

    for device_data in devices_data:
        if device_data['model'] == device:
            return device_data

    raise DeviceNotFoundException('This device does not exist')


@cache.memoize()
def get_oems():
    devices_data = get_devices_data()
    oems = {}

    for device_data in devices_data:
        oems.setdefault(device_data['oem'], []).append(device_data)

    return oems


@cache.memoize()
def get_build_types(device, romtype, after, version):
    roms = get_device_builds(device)
    roms = [x for x in roms if x['type'] == romtype]
    for rom in roms:
        rom['date'] = arrow.get(rom['date']).datetime
    if after:
        after = arrow.get(after).datetime
        roms = [x for x in roms if x['date'] > after]
    if version:
        roms = [x for x in roms if x['version'] == version]

    data = []

    for rom in roms:
        data.append({
            'id': rom['sha256'],
            'url': '%s%s' % (Config.DOWNLOAD_BASE_URL, rom['filepath']),
            'romtype': rom['type'],
            'datetime': rom['datetime'],
            'version': rom['version'],
            'filename': rom['filename'],
            'size': rom['size'],
        })
    return jsonify({'response': data})


@cache.memoize()
def get_device_version(device):
    if device == 'all':
        return None
    return get_device_builds(device)[-1]['version']


@cache.memoize()
def get_device_versions(device):
    roms = get_device_builds(device)

    versions = set()
    for rom in roms:
        versions.add(rom.version)

    return list(versions)
