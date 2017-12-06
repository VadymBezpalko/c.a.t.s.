# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from main.models import StockData
from main.serializers import StockSerializer
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
        result = parse_stock_csv(requests.post(url, data=post_data), request.data['symbol'])
    except ValueError as err:
        return JsonResponse(err.args, status=400, safe=False)

    return JsonResponse(result, safe=False)


def parse_stock_csv(data, symbol):
    text = StringIO(data.content.decode('utf-8', 'ignore'))
    reader = csv.reader(text, delimiter=',', lineterminator='\n')
    next(reader)
    next(reader)
    for id, row in enumerate(reader):
        if row[0] == 'Liczba wierszy ograniczona do 50':
            break
        serializer = StockSerializer(data={
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
            serializer.save()
        else:
            print('error at', id)
            raise ValueError(serializer.errors)

    serializer = StockSerializer(StockData.objects.all(), many=True)
    return serializer.data


@csrf_exempt
def stock_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = StockData.objects.all()
        serializer = StockSerializer(snippets, many=True)
        result = serializer.data

        sort_by = request.GET.get('sortBy', None)

        if sort_by is not None:
            result.sort(key=lambda x: x[sort_by], reverse=False)

        return JsonResponse(result, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = StockSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def stock_item_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = StockData.objects.get(pk=pk)
    except StockData.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = StockSerializer(snippet)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = StockSerializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        snippet.delete()
        return HttpResponse(status=204)