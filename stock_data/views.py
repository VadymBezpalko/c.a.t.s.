# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from stock_data.models import StockData
from stock_data.serializers import StockDataSerializer
import requests
import csv
from io import StringIO
# Create your views here.


@api_view(['POST'])
def load_stock_data(request):
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
            'date': row[0],
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
    stock_data = StockData.objects.all()
    serializer = StockDataSerializer(stock_data, many=True)
    result = serializer.data

    sort_by = request.GET.get('sortBy', None)

    if sort_by is not None:
        result.sort(key=lambda x: x[sort_by], reverse=False)

    return JsonResponse(result, safe=False)


@csrf_exempt
def stock_item_detail(request, pk):
    try:
        stock_item = StockData.objects.get(pk=pk)
    except StockData.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = StockDataSerializer(stock_item)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = StockDataSerializer(stock_item, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        stock_item.delete()
        return HttpResponse(status=204)
