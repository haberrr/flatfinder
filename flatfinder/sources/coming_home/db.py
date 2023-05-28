import mongoengine as me

from flatfinder.sources.base.db import FlatSearchResultBase, FlatBase


class ComingHomeSearchResult(FlatSearchResultBase):
    pass


class ComingHomeFlat(FlatBase):
    bedrooms = me.IntField()
    max_persons = me.IntField()
    available_from = me.DateField()
    available_to = me.DateField()
    min_period = me.IntField()
