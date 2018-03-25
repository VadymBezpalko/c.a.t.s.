from rest_framework_mongoengine import serializers
from named_entity.models import NamedEntityData


class NamedEntityDataSerializer(serializers.DynamicDocumentSerializer):
    class Meta:
        model = NamedEntityData
        fields = '__all__'
        depth = 1

