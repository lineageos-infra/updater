#!/usr/bin/env python3
#pylint: disable=line-too-long,missing-docstring,invalid-name
from __future__ import absolute_import

import json
import os
import arrow
import requests

from changelog.gerrit import GerritServer, GerritJSONEncoder
from changelog import get_changes
from custom_exceptions import DeviceNotFoundException, UpstreamApiException

from flask import Flask, jsonify, request, render_template
from flask_caching import Cache



os.environ['TZ'] = 'UTC'

app = Flask(__name__)
app.config.from_pyfile("{}/app.cfg".format(os.getcwd()))
app.json_encoder = GerritJSONEncoder

cache = Cache(app)
gerrit = GerritServer(app.config['GERRIT_URL'])

##########################
# Exception Handling
##########################

@app.errorhandler(DeviceNotFoundException)
def handle_unknown_device(error):
    oem_to_devices, device_to_oem = get_oem_device_mapping()
    return render_template("error.html", header='Whoops - this page doesn\'t exist', message=error.message, oem_to_devices=oem_to_devices, device_to_oem=device_to_oem), error.status_code

@app.errorhandler(UpstreamApiException)
def handle_upstream_exception(error):
    oem_to_devices, device_to_oem = get_oem_device_mapping()
    return render_template("error.html", header='Something went wrong', message=error.message, oem_to_devices=oem_to_devices, device_to_oem=device_to_oem), error.status_code


##########################
# Mirrorbits Interface
##########################

@cache.memoize(timeout=3600)
def get_builds():
    try:
        req = requests.get(app.config['UPSTREAM_URL'])
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
        raise DeviceNotFoundException("This device has no available builds. Please select another device.")
    return builds[device]

@cache.memoize(timeout=3600)
def get_oem_device_mapping():
    oem_to_device = {}
    device_to_oem = {}
    devices = get_device_list()
    with open('devices.json') as f:
        data = json.loads(f.read())
    for device in data:
        if device['model'] in devices:
            oem_to_device.setdefault(device['oem'], []).append(device)
            device_to_oem[device['model']] = device['oem']
    return oem_to_device, device_to_oem

@cache.memoize(timeout=3600)
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
            "id": rom['sha256'],
            "url": 'https://mirrorbits.lineageos.org{}'.format(rom['filepath']),
            "romtype": rom['type'],
            "datetime": arrow.get(rom['date']).timestamp,
            "version": rom['version'],
            "filename": rom['filename']
        })
    return jsonify({'response': data})

@cache.memoize(timeout=3600)
def get_device_version(device):
    if device == 'all':
        return None
    return get_device(device)[0]['version']

##########################
# API
##########################

@app.route('/api/v1/<string:device>/<string:romtype>/<string:incrementalversion>')
#cached via memoize on get_build_types
def index(device, romtype, incrementalversion):
    #pylint: disable=unused-argument
    after = request.args.get("after")
    version = request.args.get("version")

    return get_build_types(device, romtype, after, version)

@app.route('/api/v1/types/<string:device>/')
@cache.cached(timeout=3600)
def get_types(device):
    data = get_device(device)
    types = set(['nightly'])
    for build in data:
        types.add(build['type'])
    return jsonify({'response': list(types)})

@app.route('/api/v1/changes/<device>/')
@app.route('/api/v1/changes/<device>/<int:before>/')
@app.route('/api/v1/changes/<device>/-1/')
@cache.cached(timeout=3600)
def changes(device='all', before=-1):
    return jsonify(get_changes(gerrit, device, before, get_device_version(device), app.config.get('STATUS_URL', '#')))

@app.route('/<device>/changes/<int:before>/')
@app.route('/<device>/changes/')
@app.route('/')
@cache.cached(timeout=3600)
def show_changelog(device='all', before=-1):
    oem_to_devices, device_to_oem = get_oem_device_mapping()
    return render_template('changes.html', oem_to_devices=oem_to_devices, device_to_oem=device_to_oem, device=device, before=before, changelog=True)

@app.route('/api/v1/devices')
@cache.cached(timeout=3600)
def api_v1_devices():
    data = get_builds()
    versions = {}
    for device in data.keys():
        for build in data[device]:
            versions.setdefault(build['version'], set()).add(device)
    #pylint: disable=consider-iterating-dictionary
    for version in versions.keys():
        versions[version] = list(versions[version])
    return jsonify(versions)

##########################
# Web Views
##########################

@app.route("/<string:device>")
@cache.cached(timeout=3600)
def web_device(device):
    oem_to_devices, device_to_oem = get_oem_device_mapping()
    roms = reversed(get_device(device))

    return render_template("device.html", device=device, oem_to_devices=oem_to_devices, device_to_oem=device_to_oem, roms=roms,
                           wiki_info=app.config['WIKI_INFO_URL'], wiki_install=app.config['WIKI_INSTALL_URL'], download_base_url=app.config['DOWNLOAD_BASE_URL'])

@app.route('/favicon.ico')
def favicon():
    return ''

@app.route("/extras")
@cache.cached(timeout=3600)
def web_extras():
    oem_to_devices, device_to_oem = get_oem_device_mapping()

    return render_template("extras.html", oem_to_devices=oem_to_devices, device_to_oem=device_to_oem, extras=True)
