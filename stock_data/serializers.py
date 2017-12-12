from rest_framework_mongoengine import serializers
from stock_data.models import StockData


class StockDataSerializer(serializers.DocumentSerializer):
    class Meta:
        model = StockData
        fields = '__all__'
