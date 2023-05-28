from datetime import datetime

import mongoengine as me

from flatfinder.settings import Settings

mongo_client = me.connect(
    host=Settings.DB_HOST,
    port=Settings.DB_PORT,
    db=Settings.DB_DBNAME,
    username=Settings.DB_USER,
    password=Settings.DB_PWD,
)

db = mongo_client[Settings.DB_DBNAME]


class FlatSearchResultBase(me.Document):
    meta = {
        'abstract': True,
        'indexes': [{
            'fields': ['flat_id'],
            'unique': True,
        }],
    }

    flat_id = me.StringField(required=True, unique=True)
    url = me.URLField()
    updated_ts = me.FloatField(default=lambda: datetime.utcnow().timestamp())


class FlatBase(me.Document):
    meta = {
        'abstract': True,
        'indexes': [{
            'fields': ['flat_id'],
            'unique': True,
        }],
    }

    flat_id = me.StringField(required=True, unique=True)
    url = me.URLField(required=True)
    title = me.StringField()
    image_list = me.ListField(me.URLField())
    lat = me.FloatField()
    lon = me.FloatField()
    views = me.IntField()
    rooms = me.FloatField()
    area = me.FloatField()
    price = me.FloatField()
    district = me.StringField()
    advertiser = me.StringField()
    phone_numbers = me.ListField(me.StringField())
