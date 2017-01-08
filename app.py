from database import Rom, ApiKey

from flask import Flask, jsonify, request, abort, render_template
from flask_mongoengine import MongoEngine
from functools import wraps
from uuid import uuid4

import click
import datetime
import json
import os
import sys


app = Flask(__name__)
app.config.from_pyfile('app.cfg')

db = MongoEngine(app)

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print request.headers
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

@app.route('/api/v1/<string:device>/<string:romtype>')
def index(apiversion, device, romtype):
    after = request.args.get("after")
    version = request.args.get("version")

    roms = Rom.objects(device=device, romtype=romtype)
    if after:
        roms = roms(datetime__gt=after)
    if version:
        roms = roms(version=version)

    return roms.to_json()

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
def web_main():
    devices = sorted(Rom.objects().distinct(field="device"))
    return render_template("main.html", devices=devices)

@app.route("/<string:device>")
def web_device(device):
    devices = sorted(Rom.objects().distinct(field="device"))
    roms = Rom.objects(device=device)
    return render_template("device.html", devices=devices, roms=roms)
