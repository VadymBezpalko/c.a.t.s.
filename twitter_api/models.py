from mongoengine import *
# Create your models here.


class User(EmbeddedDocument):
    user_id = StringField()
    name = StringField()


class TwitterData(DynamicDocument):
    status_id = StringField()
    text = StringField()
    translated_text = StringField()
    retweet_count = FloatField()
    created_at = DateTimeField()
    retweeted_at = DateTimeField()
    user = EmbeddedDocumentField(User)
