from database import Rom

from flask import Flask
from flask_mongoengine import MongoEngine

import datetime
import json
import os
import sys


app = Flask(__name__)
app.config.from_pyfile('app.cfg')

db = MongoEngine(app)

@app.route("/api/<string:apiversion>/<string:device>/<string:romtype>")
def index(apiversion, device, romtype):
  if apiversion == "v1":
    r = request.get_json()
    roms = Rom.objects(device=device, romtype=romtype)

    if r:
      if 'ro.build.date.utc' in r and r['ro.build.date.utc'].isdigit():
          devicedate = datetime.datetime.utcfromtimestamp(int(r['ro.build.date.utc']))
          roms = roms(datetime__gt=devicedate)
      if 'romversion' in r:
        roms = roms(version=r['romversion'])

    return roms.to_json()

@app.route("/api/<string:apiversion>/requestfile/<string:id>")
def requestfile(apiversion=None, id=None):
  if id:
    if apiversion == "v1":
      rom = Rom.objects.get(id=id)
      if not rom['url']:
        url = config['baseurl']
        if url[-1:] != "/": url += "/"
        url += rom['filename']
      else:
        url = rom['url']

      return jsonify({ "url": url, "md5sum": rom['md5sum']})

