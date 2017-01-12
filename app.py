from database import Rom, ApiKey

from flask import Flask, jsonify, request, abort, render_template
from flask_mongoengine import MongoEngine
from flask_cache import Cache
from functools import wraps
from uuid import uuid4

import click
import datetime
import json
import os
import requests
import sys
import time

app = Flask(__name__)
app.config.from_pyfile('app.cfg')

db = MongoEngine(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(request.headers)
        if 'Apikey' in request.headers:
            if ApiKey.objects(apikey=request.headers.get('Apikey')).first():
                return f(*args, **kwargs)
        return abort(403)
    return decorated_function

def get_devices():
    return requests.get("https://raw.githubusercontent.com/LineageOS/hudson/master/getcm-devices/devices.json").json()

@app.cli.command()
@click.option('--filename', '-f', 'filename', required=True)
@click.option('--device', '-d', 'device', required=True)
@click.option('--version', '-v', 'version', required=True)
@click.option('--datetime', '-t', 'datetime', required=True)
@click.option('--romtype', '-r', 'romtype', required=True)
@click.option('--md5sum', '-m', 'md5sum', required=True)
@click.option('--url', '-u', 'url', required=True)
@click.option('--available', '-a', 'available', default=False)
def addrom(filename, device, version, datetime, romtype, md5sum, url, available):
    Rom(filename=filename, datetime=datetime, device=device, version=version, romtype=romtype, md5sum=md5sum, url=url, available=available).save()

@app.cli.command()
@click.option("--comment", 'comment', required=False)
@click.option("--remove", "remove", default=False)
@click.option("--print", "echo", flag_value='echo', default=False)
def add_api_key(comment, remove, echo):
    if echo:
        for i in ApiKey.objects():
            print(i.apikey, i.comment)
    elif remove:
        for i in ApiKey.objects(apikey=apikey):
            i.delete()
    elif comment:
        key = uuid4().hex
        ApiKey(apikey=key, comment=comment).save()
        print(key)
    else:
        print("comment or print required")

@app.route('/api/v1/<string:device>/<string:romtype>/<string:incrementalversion>')
def index(device, romtype, incrementalversion):
    after = request.args.get("after")
    version = request.args.get("version")

    roms = Rom.objects(device=device, romtype=romtype, available=True)
    if after:
        roms = roms(datetime__gt=after)
    if version:
        roms = roms(version=version)

    data = []

    for rom in roms:
        data.append({
            "id": str(rom.id),
            "url": rom.url,
            "romtype": rom.romtype,
            "datetime": int(time.mktime(rom.datetime.timetuple())),
            "version": rom.version,
            "filename": rom.filename
        })
    return jsonify({'response': data })

@app.route('/api/v1/requestfile/<string:file_id>')
def requestfile(file_id):
    rom = Rom.objects.get(id=id)
    if not rom['url']:
        url = config['baseurl']
        if url[-1:] != '/':
            url += '/'
        url += rom['filename']
    else:
        url = rom['url']

    return jsonify({ 'url': url, 'md5sum': rom['md5sum']})

@app.route("/api/v1/auth")
@api_key_required
def test_auth():
    return "pass"

@app.route('/api/v1/add_build', methods=['POST',])
@api_key_required
def add_build():
    data = request.get_json()
    #validate
    if not 'filename' in data or not 'device' in data or not 'version' in data \
       or not 'datetime' in data or not 'md5sum' in data or not 'url' in data \
       or not 'romtype' in data:
       return "malformed json", 500

    rom = Rom(**data)
    rom.available = False
    rom.save()
    return "ok", 200

@app.route('/')
@cache.cached(timeout=3600)
def web_main():
    devices = get_devices()
    active_devices = sorted(Rom.objects().distinct(field="device"))
    devices = [x for x in devices if x['model'] in active_devices]
    oems = sorted(list(set([x['oem'] for x in devices])))
    #devices = sorted(Rom.objects().distinct(field="device"))
    return render_template("main.html", oems=oems, devices=devices)

@app.route("/<string:device>")
@cache.cached(timeout=3600)
def web_device(device):
    #devices = sorted(Rom.objects().distinct(field="device"))
    devices = get_devices()
    active_devices = sorted(Rom.objects().distinct(field="device"))
    devices = [x for x in devices if x['model'] in active_devices]
    oems = sorted(list(set([x['oem'] for x in devices])))

    roms = Rom.objects(device=device)

    active_oem = [x['oem'] for x in devices if x['model'] == device]
    active_oem = active_oem[0] if active_oem else None
    
    return render_template("device.html", active_oem=active_oem, active_device=device, oems=oems, devices=devices, roms=roms)
