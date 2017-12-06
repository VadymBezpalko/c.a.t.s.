from rest_framework import serializers
from stock_data.models import StockData


class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = ('id', 'symbol', 'date', 'open', 'min', 'max', 'close', 'change', 'value')
