# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
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

    result = parse_stock_csv(requests.post(url, data=post_data), request.data['symbol'])

    return Response(result)


def parse_stock_csv(data, symbol):
    text = StringIO(data.content.decode('utf-8', 'ignore'))
    reader = csv.reader(text, delimiter=',', lineterminator='\n')
    result = []
    next(reader)
    next(reader)
    for row in reader:
        if row[0] == 'Liczba wierszy ograniczona do 50':
            break
        print(row)
        result.append(StockData(
            symbol=symbol,
            date=row[0],
            open=row[1],
            min=row[2],
            max=row[3],
            close=row[4],
            change=row[5],
            value=row[6]
        ))

    serializer = StockSerializer(result, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def stock_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = StockData.objects.all()
        serializer = StockSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

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