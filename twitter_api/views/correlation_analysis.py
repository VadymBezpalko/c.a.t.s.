from rest_framework.decorators import api_view
from stock_data.models import StockData
from twitter_api.models import TwitterData
import common.util as util


@api_view(['POST'])
def get_pearson_correlation(request):
    twitter_query = TwitterData.objects(
        search_term=request.data['search_term'],
        created_at__gt=request.data['from'],
        created_at__lt=request.data['to']
    )
    stock_query = StockData.objects(
        symbol=request.data['symbol'],
        date__gt=request.data['from'],
        date__lt=request.data['to']
    )
    twitter_messages = util.get_serialized_data(twitter_query, 'twitter')
    stock_data = util.get_serialized_data(stock_query, 'stock')

    print('twitter data length', twitter_messages)
    print('stock data length', stock_data)

