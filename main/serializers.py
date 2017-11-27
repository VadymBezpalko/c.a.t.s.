from rest_framework import serializers
from main.models import StockData


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = ('id', 'symbol', 'date', 'open', 'min', 'max', 'close', 'change', 'value')
