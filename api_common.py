import json
import os

import arrow
import requests

from flask import jsonify
from changelog import get_timestamp
from config import Config
from custom_exceptions import UpstreamApiException, DeviceNotFoundException

import extensions

@extensions.cache.memoize()
def get_builds():
    try:
        req = requests.get(Config.UPSTREAM_URL, timeout=60)
        if req.status_code != 200:
            raise UpstreamApiException('Unable to contact upstream API')
        return json.loads(req.text)
    except Exception as e:
        print(e)
        raise UpstreamApiException('Unable to contact upstream API')


def get_devices_with_builds():
    return get_builds().keys()

@extensions.cache.memoize()
def get_device_builds(device):
    builds = get_builds()
    if device not in builds:
        return []

    device_builds = builds[device]
    device_builds.sort(key=lambda b: b['datetime'], reverse=True)

    def sorting_key(item):
        filename = item['filename']
        if filename.endswith(".zip"):
            return 1, filename
        elif filename.endswith(".img"):
            return 2, filename
        else:
            return 3, filename

    for build in device_builds:
        build['files'] = sorted(build['files'], key=sorting_key)

    return device_builds

@extensions.cache.memoize()
def get_build_roster():
    devices = []

    if os.path.isfile(Config.LINEAGE_BUILD_TARGETS_PATH):
        with open(Config.LINEAGE_BUILD_TARGETS_PATH) as f:
            for line in f.readlines():
                if line and not line.startswith('#'):
                    devices.append(line.split()[0])
    elif Config.OFFICIAL_LINEAGE_BUILD_TARGETS_URL:
        for line in requests.get(Config.OFFICIAL_LINEAGE_BUILD_TARGETS_URL, timeout=60).text.splitlines():
            if line and not line.startswith('#'):
                devices.append(line.split()[0])

    return devices

@extensions.cache.memoize()
def get_devices_data():
    devices_data = []

    if os.path.isfile(Config.DEVICES_JSON_PATH):
        with open(Config.DEVICES_JSON_PATH) as f:
            devices_data += json.loads(f.read())
    else:
        devices_data += requests.get(Config.OFFICIAL_DEVICES_JSON_URL, timeout=60).json()

    if os.path.isfile(Config.DEVICES_LOCAL_JSON_PATH):
        with open(Config.DEVICES_LOCAL_JSON_PATH) as f:
            devices_data += json.loads(f.read())

    build_roster = get_build_roster()
    devices_with_builds = get_devices_with_builds()

    devices = []

    for device_data in devices_data:
        if device_data['model'] in devices_with_builds or device_data['model'] in build_roster:
            devices.append(device_data)

    return devices


@extensions.cache.memoize()
def get_device_data(device):
    devices_data = get_devices_data()

    for device_data in devices_data:
        if device_data['model'] == device:
            return device_data

    raise DeviceNotFoundException('This device does not exist')


@extensions.cache.memoize()
def get_oems():
    devices_data = get_devices_data()
    oems = {}

    for device_data in devices_data:
        oems.setdefault(device_data['oem'], []).append(device_data)

    return oems


@extensions.cache.memoize()
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
            'id': rom['files'][0]['sha256'],
            'url': '%s%s' % (Config.DOWNLOAD_BASE_URL, rom['files'][0]['filepath']),
            'romtype': rom['type'],
            'datetime': rom['datetime'],
            'version': rom['version'],
            'filename': rom['files'][0]['filename'],
            'size': rom['files'][0]['size'],
        })
    return jsonify({'response': data})


@extensions.cache.memoize()
def get_device_version(device):
    if device == 'all':
        return None
    return get_device_builds(device)[-1]['version']


@extensions.cache.memoize()
def get_device_versions(device):
    roms = get_device_builds(device)

    versions = set()
    for rom in roms:
        versions.add(rom['version'])

    return list(versions)

@extensions.cache.memoize()
def group_changes_by_build(changes, builds, versions):
    builds_changes = []

    builds.sort(key=lambda b: b['datetime'])

    for build in builds:
        build_changes = {
            'build': build,
            'items': []
        }

        for change in changes:
            submit_timestamp = get_timestamp(change.submitted)
            if submit_timestamp <= build['datetime'] and build['version'] in change.branch:
                build_changes['items'].append(change)

        builds_changes.insert(0, build_changes)

        changes = [c for c in changes if c not in build_changes['items']]

    for version in versions:
        build_changes = {
            'build': {
                'filename': 'next',
                'version': version,
            },
            'items': []
        }

        for change in changes:
            if version in change.branch:
                build_changes['items'].append(change)

        builds_changes.insert(0, build_changes)

    return builds_changes
