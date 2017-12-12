# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mongoengine import Document, fields


# Create your models here.

class StockData(Document):
    symbol = fields.StringField(required=True)
    date = fields.StringField()
    open = fields.FloatField()
    min = fields.FloatField()
    max = fields.FloatField()
    close = fields.FloatField()
    change = fields.FloatField()
    value = fields.FloatField()
