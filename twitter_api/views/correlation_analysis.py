from rest_framework.decorators import api_view
from stock_data.models import StockData
from twitter_api.models import TwitterData
from django.http import JsonResponse
import numpy
import common.util as util


@api_view(['POST'])
def get_pearson_correlation(request):
    twitter_query = TwitterData.objects(
        search_term=request.data['search_term'],
        created_at__gte=request.data['from'],
        created_at__lte=request.data['to']
    ).order_by('created_at')

    stock_query = StockData.objects(
        symbol=request.data['symbol'],
        date__gte=request.data['from'],
        date__lte=request.data['to']
    ).order_by('date')

    twitter_messages = util.get_serialized_data(twitter_query, 'twitter')
    stock_data = util.get_serialized_data(stock_query, 'stock')
    summarized_messages = util.summarize_twitter_data_by_day(twitter_messages)

    # temp list containing strings with available stock dates
    # used for eliminating "non stock days" messages - weekend messages
    trimmed_twitter_messages = []
    trimmed_stock_data = []
    strings_list = []
    for stock in stock_data:
        strings_list.append(stock['date'])

    # eliminating weekend messages
    for message in summarized_messages:
        for item in strings_list:
            if message['created_at'] in item:
                trimmed_twitter_messages.append(message['average_sentimental'])
                trimmed_stock_data.append(next((x['close'] for x in stock_data if x['date'] == item), None))

    correlation = numpy.corrcoef(trimmed_twitter_messages, trimmed_stock_data)[0, 1]

    return JsonResponse(correlation, safe=False)


@api_view(['POST'])
def get_pearson_correlation_2(request):
    twitter_query = TwitterData.objects(
        search_term=request.data['search_term'],
        created_at__gte=request.data['from'],
        created_at__lte=request.data['to']
    ).order_by('created_at')

    stock_query = StockData.objects(
        symbol=request.data['symbol'],
        date__gte=request.data['from'],
        date__lte=request.data['to']
    ).order_by('date')

    twitter_messages = util.get_serialized_data(twitter_query, 'twitter')
    stock_data = util.get_serialized_data(stock_query, 'stock')
    summarized_messages = util.count_daily_messages(twitter_messages)

    # temp list containing strings with available stock dates
    # used for eliminating "non stock days" messages - weekend messages
    trimmed_twitter_messages = []
    trimmed_stock_data = []
    strings_list = []
    for stock in stock_data:
        strings_list.append(stock['date'])

    # eliminating weekend messages
    for message in summarized_messages:
        for item in strings_list:
            if message['date'] in item:
                trimmed_twitter_messages.append(message['number'])
                trimmed_stock_data.append(next((x['close'] for x in stock_data if x['date'] == item), None))

    correlation = numpy.corrcoef(trimmed_twitter_messages, trimmed_stock_data)[0, 1]

    return JsonResponse(correlation, safe=False)
