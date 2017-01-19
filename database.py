from mongoengine import Document, BooleanField, DateTimeField, StringField

from datetime import datetime, timedelta

class Rom(Document):
    filename = StringField(required=True)
    datetime = DateTimeField(required=True, default=datetime.now())
    device = StringField(required=True)
    version = StringField(required=True)
    romtype = StringField(required=True)
    md5sum = StringField(required=True)
    url = StringField()

    @classmethod
    def get_roms(cls, device, romtype=None, before=3600):
        if romtype:
            return cls.objects(device=device, romtype=romtype, datetime__lt=datetime.now()-timedelta(seconds=before))
        else:
            return cls.objects(device=device, datetime__lt=datetime.now()-timedelta(seconds=before))

    @classmethod
    def get_devices(cls):
        #TODO change this to an aggregate
        cls.objects().distinct(field="device")

class Device(Document):
    model = StringField(required=True, unique=True)
    oem = StringField(required=True)
    name = StringField(required=True)
    image = StringField(required=False)
    has_recovery = BooleanField(required=False, default=True)
    wiki = StringField(required=False)

    @classmethod
    def get_devices(cls):
        return cls.objects()

class ApiKey(Document):
    apikey = StringField(required=True)
    comment = StringField(required=False)
