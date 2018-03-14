from rest_framework.decorators import api_view
from stock_data.models import StockData
from twitter_api.models import TwitterData
from django.http import JsonResponse

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
    )
    twitter_messages = util.get_serialized_data(twitter_query, 'twitter')
    stock_data = util.get_serialized_data(stock_query, 'stock')
    summarized_messages = util.summarize_twitter_data(twitter_messages)
    print('twitter data length', len(twitter_messages))
    print('summarized twitter data length', len(summarized_messages))
    print('stock data length', len(stock_data))

    return JsonResponse([twitter_messages, stock_data], safe=False)
