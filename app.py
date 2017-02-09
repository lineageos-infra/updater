from database import Rom, ApiKey, Device

from flask import Flask, jsonify, request, abort, render_template
from flask_mongoengine import MongoEngine
from flask_caching import Cache
from functools import wraps
from pydoc import locate
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
cache = Cache(app)

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(request.headers)
        if 'Apikey' in request.headers:
            if ApiKey.objects(apikey=request.headers.get('Apikey')).first():
                return f(*args, **kwargs)
        return abort(403)
    return decorated_function

@app.cli.command()
@click.option('--filename', '-f', 'filename', required=True)
@click.option('--device', '-d', 'device', required=True)
@click.option('--version', '-v', 'version', required=True)
@click.option('--datetime', '-t', 'datetime', required=True)
@click.option('--romtype', '-r', 'romtype', required=True)
@click.option('--md5sum', '-m', 'md5sum', required=True)
@click.option('--url', '-u', 'url', required=True)
def addrom(filename, device, version, datetime, romtype, md5sum, url):
    Rom(filename=filename, datetime=datetime, device=device, version=version, romtype=romtype, md5sum=md5sum, url=url).save()

@app.cli.command()
@click.option('--filename', '-f', 'filename', required=True)
def delrom(filename):
    Rom.objects(filename=filename).delete()

@app.cli.command()
@click.option("--comment", 'comment', required=False)
@click.option("--remove", "remove", default=False)
@click.option("--print", "echo", flag_value='echo', default=False)
def api_key(comment, remove, echo):
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

@app.cli.command()
def import_devices():
    with open("devices.json", "r") as f:
        data = json.load(f)
        for device in data:
            d = Device.objects(model=device['model'])
            if d:
                d.update(**device)
            else:
                Device(**device).save()
    if os.path.isfile("devices_local.json"):
        with open("devices_local.json", "r") as f:
            data = json.load(f)
            for device in data:
                d = Device.objects(model=device['model'])
                if d:
                    d.update(**device)
                else:
                    Device(**device).save()

@app.route('/api/v1/<string:device>/<string:romtype>/<string:incrementalversion>')
def index(device, romtype, incrementalversion):
    after = request.args.get("after")
    version = request.args.get("version")

    roms = Rom.get_roms(device=device, romtype=romtype, before=app.config['BUILD_SYNC_TIME'])
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

@app.route('/api/v1/types/<string:device>/')
def get_types(device):
    types = set(["nightly"])
    for rtype in Rom.get_types(device):
        types.add(rtype)
    return jsonify({'response': list(types)})

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
    validate = {"filename": "str", "device": "str", "version": "str", "md5sum": "str", "url": "str", "romtype": "str"}

    #bad data sent
    if not data:
        return jsonify(validate), 400
    #validate keys all exist
    for key in validate.keys():
        if key not in data:
            return jsonify(validate), 406

    # validate types
    for key in validate.keys():
        try:
            locate(validate[key])(data[key])
        except:
            return jsonify({"error": "{} must be parseable by python's {} class".format(key, validate[key])}), 406
    rom = Rom(**data)
    rom.save()
    return "ok", 200

@app.route('/api/v1/devices')
@cache.cached(timeout=3600)
def api_v1_devices():
    return jsonify(Rom.get_current_devices_by_version())

@app.route('/api/v1/<string:filename>', methods=['DELETE',])
@api_key_required
def api_v1_delete_file(filename):
    Rom.objects(filename=filename).delete()
    return '', 200

@app.route('/api/v1/purgecache', methods=['POST',])
@api_key_required
def purge_cache():
    cache.clear()
    return 'ok', 200

@app.route('/')
@cache.cached(timeout=3600)
def web_main():
    devices = sorted([x for x in Device.get_devices() if x['model'] in Rom.get_devices()], key=lambda device: device['name'])
    oems = sorted(list(set([x['oem'] for x in devices])))
    return render_template("main.html", oems=oems, devices=devices)

@app.route("/<string:device>")
@cache.cached(timeout=3600)
def web_device(device):
    devices = sorted([x for x in Device.get_devices() if x['model'] in Rom.get_devices()], key=lambda device: device['name'])
    oems = sorted(list(set([x['oem'] for x in devices])))

    roms = Rom.get_roms(device=device, before=app.config['BUILD_SYNC_TIME'])

    active_oem = [x['oem'] for x in devices if x['model'] == device]
    active_oem = active_oem[0] if active_oem else None

    return render_template("device.html", active_oem=active_oem, active_device=device, oems=oems, devices=devices, roms=roms)

@app.route("/extras")
@cache.cached(timeout=3600)
def web_extras():
    devices = sorted([x for x in Device.get_devices() if x['model'] in Rom.get_devices()], key=lambda device: device['name'])
    oems = sorted(list(set([x['oem'] for x in devices])))

    return render_template("extras.html", oems=oems, devices=devices, extras=True)
