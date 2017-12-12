from rest_framework_mongoengine import serializers
from twitter_api.models import TwitterData


class TwitterDataSerializer(serializers.DynamicDocumentSerializer):
    class Meta:
        model = TwitterData
        fields = '__all__'
        depth = 2

