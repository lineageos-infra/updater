#!/usr/bin/python3

import argparse
import json
import os
import sys

from classes import *
from mongoengine import *

configfile = "config.json"

if not os.path.isfile(configfile):
  print("Could not find " + configfile + " aborting!")
  sys.exit()

with open(configfile) as config_file:		
  config = json.load(config_file)

def getargs():
  parser = argparse.ArgumentParser()
  parser.add_argument('-f', '--filename', required=True)
  parser.add_argument('-d', '--device', required=True)
  parser.add_argument('-v', '--version', required=True)
  parser.add_argument('-dt', '--datetime', required=True)
  parser.add_argument('-t', '--romtype', required=True)
  parser.add_argument('-m', '--md5sum', required=True)
  parser.add_argument('-u', '--url', required=False)
  return parser.parse_args()

def addrom(filename, datetime, device, version, romtype, md5sum, url=None):
  connect('lineage_updater', host=config['dbhost'])
  Rom(filename=filename, datetime=datetime, device=device, version=version, romtype=romtype, md5sum=md5sum, url=url).save()

if __name__ == "__main__":
  args = getargs()
  addrom(args.filename, args.datetime, args.device, args.version, args.romtype, args.md5sum, args.url)
