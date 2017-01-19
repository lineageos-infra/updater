from mongoengine import Document, BooleanField, DateTimeField, StringField

class Rom(Document):
    filename = StringField(required=True)
    datetime = DateTimeField(required=True)
    device = StringField(required=True)
    version = StringField(required=True)
    romtype = StringField(required=True)
    md5sum = StringField(required=True)
    url = StringField()

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
