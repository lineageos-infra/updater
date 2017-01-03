#!/usr/bin/python3

from mongoengine import *

class Rom(Document):
  filename = StringField()
  datetime = DateTimeField(required=True)
  device = StringField()
  version = StringField()
  romtype = StringField()
  url = StringField()
  md5sum = StringField()
