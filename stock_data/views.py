# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from stock_data.models import StockData
from stock_data.serializers import StockDataSerializer
import requests
import csv
from io import StringIO
from datetime import datetime
import common.util as util


@api_view(['POST'])
def fetch_stock_data(request):
    url = 'https://www.money.pl/gielda/archiwum/spolki/'

    post_data = {
        'symbol': request.data['symbol'],
        'od': request.data['start_date'],
        'do': request.data['end_date'],
        'format': request.data['format']
    }

    try:
        result = save_stock_csv(requests.post(url, data=post_data), request.data['symbol'])
    except ValueError as err:
        return JsonResponse(err.args, status=400, safe=False)

    return JsonResponse(result, safe=False)


def save_stock_csv(data, symbol):
    text = StringIO(data.content.decode('utf-8', 'ignore'))
    reader = csv.reader(text, delimiter=',', lineterminator='\n')
    next(reader)
    next(reader)
    for id, row in enumerate(reader):
        if row[0] == 'Liczba wierszy ograniczona do 50':
            break
        serializer = StockDataSerializer(data={
            'symbol': symbol,
            'date': datetime.strptime(row[0], '%Y-%m-%d'),
            'open': row[1].replace(',', '.'),
            'min': row[2].replace(',', '.'),
            'max': row[3].replace(',', '.'),
            'close': row[4].replace(',', '.'),
            'change': row[5].replace(',', '.'),
            'value': row[6].replace(',', '.')
        })
        if serializer.is_valid():
            try:
                temp = StockData.objects.get(symbol=symbol, date=row[0])
                serializer = temp
            except StockData.DoesNotExist:
                pass

            serializer.save()
        else:
            print('error at', id)
            raise ValueError(serializer.errors)

    serializer = StockDataSerializer(StockData.objects.all(), many=True)
    return serializer.data


@csrf_exempt
def get_stock_list(request):
    filter_by_name = request.GET.get('symbol')

    if filter_by_name is not None:
        stock_data = StockData.objects(
            symbol=filter_by_name,
            date__gte=request.GET.get('from'),
            date__lte=request.GET.get('to')
        )
    else:
        stock_data = StockData.objects.all()

    result = util.get_serialized_data(stock_data.order_by('date'), 'stock')

    return JsonResponse(result, safe=False)

