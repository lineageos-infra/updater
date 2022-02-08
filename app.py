#!/usr/bin/env python3
#pylint: disable=line-too-long,missing-docstring,invalid-name
from __future__ import absolute_import

import json
import os
from time import time, strftime

import arrow
import requests
from changelog.gerrit import GerritServer, GerritJSONEncoder
from changelog import get_changes
from config import Config
from custom_exceptions import DeviceNotFoundException, UpstreamApiException
from flask import Flask, jsonify, request, render_template, Response
from flask_caching import Cache
from prometheus_client import multiprocess, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, Counter, Histogram



app = Flask(__name__)
app.config.from_object("config.Config")
app.json_encoder = GerritJSONEncoder

cache = Cache(app)
gerrit = GerritServer(app.config['GERRIT_URL'])

extras_data = json.loads(open(app.config['EXTRAS_BLOB'], "r").read())

##########################
# jinja2 globals
##########################

def version():
    return os.environ.get("VERSION", "dev")[:6]

app.jinja_env.globals.update(version=version)

##########################
# Metrics!
##########################
REQUEST_LATENCY = Histogram("flask_request_latency_seconds", "Request Latency", ['method', 'endpoint'])
REQUEST_COUNT = Counter("flask_request_count", "Request Count", ["method", "endpoint", "status"])

@app.before_request
def start_timer():
    request.stats_start = time()

@app.after_request
def stop_timer(response):
    delta = time() - request.stats_start
    REQUEST_LATENCY.labels(request.method, request.endpoint).observe(delta) #pylint: disable=no-member
    REQUEST_COUNT.labels(request.method, request.endpoint, response.status_code).inc() #pylint: disable=no-member
    return response

@app.route('/metrics')
def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)

##########################
# Exception Handling
##########################

@app.errorhandler(DeviceNotFoundException)
def handle_unknown_device(error):
    if request.path.startswith('/api/'):
        return jsonify({'response': []})
    oem_to_devices, device_to_oem, _ = get_oem_device_mapping()
    return render_template("error.html", header='Whoops - this page doesn\'t exist', message=error.message, oem_to_devices=oem_to_devices, device_to_oem=device_to_oem), error.status_code

@app.errorhandler(UpstreamApiException)
def handle_upstream_exception(error):
    if request.path.startswith('/api/'):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    oem_to_devices, device_to_oem, _ = get_oem_device_mapping()
    return render_template("error.html", header='Something went wrong', message=error.message, oem_to_devices=oem_to_devices, device_to_oem=device_to_oem), error.status_code


##########################
# Mirrorbits Interface
##########################

@cache.memoize()
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
            offer_recovery[device['model']] = device.get('lineage_recovery', True)
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
            "id": rom['sha256'],
            "url": '{}{}'.format(app.config['DOWNLOAD_BASE_URL'], rom['filepath']),
            "romtype": rom['type'],
            "datetime": rom['datetime'],
            "version": rom['version'],
            "filename": rom['filename'],
            "size": rom['size'],
        })
    return jsonify({'response': data})

@cache.memoize()
def get_device_version(device):
    if device == 'all':
        return None
    return get_device(device)[-1]['version']

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
@cache.cached()
def get_types(device):
    data = get_device(device)
    types = set(['nightly'])
    for build in data:
        types.add(build['type'])
    return jsonify({'response': list(types)})

@app.route('/api/v1/changes/<device>/')
@app.route('/api/v1/changes/<device>/<int:before>/')
@app.route('/api/v1/changes/<device>/-1/')
@cache.cached()
def changes(device='all', before=-1):
    return jsonify(get_changes(gerrit, device, before, get_device_version(device), app.config.get('STATUS_URL', '#')))

@app.route('/<device>/changes/<int:before>/')
@app.route('/<device>/changes/')
@app.route('/')
@cache.cached()
def show_changelog(device='all', before=-1):
    oem_to_devices, device_to_oem, _ = get_oem_device_mapping()
    return render_template('changes.html', oem_to_devices=oem_to_devices, device_to_oem=device_to_oem, device=device, before=before, changelog=True)

@app.route('/api/v1/devices')
@cache.cached()
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

@app.context_processor
def inject_year():
    return dict(year=strftime("%Y"))

@app.route("/<string:device>")
@cache.cached()
def web_device(device):
    oem_to_devices, device_to_oem, offer_recovery = get_oem_device_mapping()
    roms = get_device(device)[::-1]
    has_recovery = any([True for rom in roms if 'recovery' in rom ]) and offer_recovery[device]

    return render_template("device.html", device=device, oem_to_devices=oem_to_devices, device_to_oem=device_to_oem, roms=roms, has_recovery=has_recovery,
                           wiki_info=app.config['WIKI_INFO_URL'], wiki_install=app.config['WIKI_INSTALL_URL'], download_base_url=app.config['DOWNLOAD_BASE_URL'])

@app.route('/favicon.ico')
def favicon():
    return ''

@app.route("/extras")
@cache.cached()
def web_extras():
    oem_to_devices, device_to_oem, _ = get_oem_device_mapping()

    return render_template("extras.html", oem_to_devices=oem_to_devices, device_to_oem=device_to_oem, extras=True, data=extras_data)
