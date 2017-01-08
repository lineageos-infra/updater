#!/usr/bin/python3

from mongoengine import *

class Rom(Document):
  filename = StringField(required=True)
  datetime = DateTimeField(required=True)
  device = StringField(required=True)
  version = StringField(required=True)
  romtype = StringField(required=True)
  md5sum = StringField(required=True)
  url = StringField()
