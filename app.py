#!/usr/bin/env python3
from __future__ import absolute_import

import json
import os
from time import time, strftime

from flask import Flask, jsonify, request, render_template, Response
from prometheus_client import multiprocess, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, Counter, Histogram

from api_common import get_device_builds, get_oems, get_device_data
from caching import cache
from custom_exceptions import DeviceNotFoundException, UpstreamApiException
from config import Config
from api_v1 import api as api_v1

app = Flask(__name__)
app.config.from_object('config.FlaskConfig')
app.register_blueprint(api_v1, url_prefix='/api/v1')

cache.init_app(app)

extras_data = json.loads(open(Config.EXTRAS_BLOB, 'r').read())


##########################
# Jinja2 globals
##########################

def version():
    return os.environ.get('VERSION', 'dev')[:6]


app.jinja_env.globals.update(version=version)


##########################
# Metrics
##########################
REQUEST_LATENCY = Histogram('flask_request_latency_seconds', 'Request Latency', ['method', 'endpoint'])
REQUEST_COUNT = Counter('flask_request_count', 'Request Count', ['method', 'endpoint', 'status'])


@app.before_request
def start_timer():
    request.stats_start = time()


@app.after_request
def stop_timer(response):
    delta = time() - request.stats_start
    REQUEST_LATENCY.labels(request.method, request.endpoint).observe(delta)
    REQUEST_COUNT.labels(request.method, request.endpoint, response.status_code).inc()
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
    oems = get_oems()
    return render_template('error.html', header='Whoops - this page doesn\'t exist', message=error.message,
                           oems=oems), error.status_code


@app.errorhandler(UpstreamApiException)
def handle_upstream_exception(error):
    if request.path.startswith('/api/'):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    oems = get_oems()
    return render_template('error.html', header='Something went wrong', message=error.message,
                           oems=oems), error.status_code


##########################
# Web Views
##########################

@app.route('/<device>/changes/<int:before>/')
@app.route('/<device>/changes/')
@app.route('/')
@cache.cached()
def show_changelog(device='all', before=-1):
    oems = get_oems()
    device_data = get_device_data(device)

    return render_template('changes.html', oems=oems, active_device_data=device_data,
                           before=before, changelog=True)


@app.context_processor
def inject_year():
    return dict(year=strftime('%Y'))


@app.route('/<string:device>')
@cache.cached()
def web_device(device):
    oems = get_oems()
    device_data = get_device_data(device)
    roms = get_device_builds(device)[::-1]
    has_recovery = any([True for rom in roms if 'recovery' in rom]) and device_data.get('lineage_recovery', False)

    return render_template('device.html', oems=oems, active_device_data=device_data,
                           roms=roms, has_recovery=has_recovery,
                           wiki_info=Config.WIKI_INFO_URL, wiki_install=Config.WIKI_INSTALL_URL,
                           download_base_url=Config.DOWNLOAD_BASE_URL)


@app.route('/extras')
@cache.cached()
def web_extras():
    oems = get_oems()

    return render_template('extras.html', oems=oems, active_device_data=None, extras=True,
                           data=extras_data)
