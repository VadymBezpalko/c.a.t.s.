from __future__ import unicode_literals
from mongoengine import Document, fields


class NamedEntityData(Document):
    text = fields.StringField()
    search_term = fields.StringField()
    pos_quantity = fields.IntField()
    neg_quantity = fields.IntField()
