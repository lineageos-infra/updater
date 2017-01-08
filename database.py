from mongoengine import Document, BooleanField, DateTimeField, StringField

class Rom(Document):
    filename = StringField(required=True)
    datetime = DateTimeField(required=True)
    device = StringField(required=True)
    version = StringField(required=True)
    romtype = StringField(required=True)
    md5sum = StringField(required=True)
    available = BooleanField(required=False, default=False)
    url = StringField()
