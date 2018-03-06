from mongoengine import *
# Create your models here.


class User(EmbeddedDocument):
    user_id = StringField()
    name = StringField()


class Sentimental(EmbeddedDocument):
    score = FloatField()
    comparative = FloatField()
    polarity = FloatField()
    subjectivity = FloatField()


class TwitterData(DynamicDocument):
    status_id = StringField()
    search_term = StringField()
    text = StringField()
    translated_text = StringField()
    retweet_count = FloatField()
    created_at = DateTimeField()
    retweeted_at = DateTimeField(null=True)
    user = EmbeddedDocumentField(User)
    sentimental = EmbeddedDocumentField(Sentimental)
    entities = ListField()
