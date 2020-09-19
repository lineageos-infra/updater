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


def get_device_list():
    return get_builds().keys()


def get_device(device):
    builds = get_builds()
    if device not in builds:
        raise DeviceNotFoundException('This device has no available builds. Please select another device.')
    return builds[device]


@cache.memoize()
def get_oem_device_mapping():
    oem_to_device = {}
    device_to_oem = {}
    offer_recovery = {}
    devices = get_device_list()
    if os.path.isfile(Config.DEVICES_JSON_PATH):
        with open(Config.DEVICES_JSON_PATH) as f:
            data = json.loads(f.read())
    else:
        data = requests.get('https://raw.githubusercontent.com/LineageOS/hudson/master/updater/devices.json').json()
    if os.path.isfile('devices_local.json'):
        with open('devices_local.json') as f:
            data += json.loads(f.read())
    for device in data:
        if device['model'] in devices:
            oem_to_device.setdefault(device['oem'], []).append(device)
            device_to_oem[device['model']] = device['oem']
            offer_recovery[device['model']] = device.get('lineage_recovery', False)
    return oem_to_device, device_to_oem, offer_recovery


@cache.memoize()
def get_build_types(device, romtype, after, version):
    roms = get_device(device)
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
    return get_device(device)[-1]['version']
