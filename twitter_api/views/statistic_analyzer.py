from rest_framework.decorators import api_view
from twitter_api.models import TwitterData
from django.http import JsonResponse
import common.util as util
from collections import Counter


@api_view(['GET'])
def get_retweets_stat(request):
    twitter_query = TwitterData.objects.all()
    twitter_messages = util.get_serialized_data(twitter_query, 'twitter')

    c = Counter(message['retweet_count'] for message in twitter_messages)
    print(c)

    return JsonResponse(c, safe=False)
