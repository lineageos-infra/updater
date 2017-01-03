#!/usr/bin/python3

import json
import local_config
import os
import sys

from classes import *
from flask import *
from mongoengine import *

app = Flask(__name__)
app.config.from_object(local_config)

configfile = "config.json"

if not os.path.isfile(configfile):
  print("Could not find " + configfile + " aborting!")
  sys.exit()

with open(configfile) as config_file:
  config = json.load(config_file)

connect('lineage_updater', host=config['dbhost'])

@app.route("/api/<string:apiversion>/<string:device>/<string:romtype>/<string:romversion>")
@app.route("/api/<string:apiversion>/<string:device>/<string:romtype>")
def index(apiversion, device, romtype, romversion=None):
  if apiversion == "v1":
    if romversion:
      roms = Rom.objects(device=device, romtype=romtype, version=romversion)
    else:
      roms = Rom.objects(device=device, romtype=romtype)

    return roms.to_json()

@app.route("/api/<string:apiversion>/requestfile/<string:id>")
def requestfile(apiversion=None, id=None):
  if id:
    if apiversion == "v1":
      rom = Rom.objects.get(id=id)
      if not rom['url']:
        url = config['baseurl'] + "/" + rom['filename']
      else:
        url = rom['url']

      return jsonify({ "url": url, "md5sum": rom['md5sum']})

app.run(host='0.0.0.0')
