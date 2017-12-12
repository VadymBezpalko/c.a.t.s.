import time
from twython import Twython
from django.http import JsonResponse
from rest_framework.decorators import api_view

from twitter_api.serializers import TwitterDataSerializer
from twitter_api.models import TwitterData
# Create your views here.

API_KEY = 'gmYLVJ21JFa0YB8zhIo71GJ9m'
API_SECRET = '3CB6gOeqqpYLQ1Y1rlkVbvriCQjdyg3pXfq3kSpdjIR9kToSxj'
TOKEN_KEY = '3365870121-PcBq6nthIQRWrcGwNRg1xUW5LGaOJ9CLd8262Ie'
TOCKET_SECRET_KEY = 'AVUuT3QGFPK6x5icab7aSdI9fjC0Cje2tkLVsnIhfX9yI'


api = Twython(API_KEY, API_SECRET, TOKEN_KEY, TOCKET_SECRET_KEY)


@api_view(['POST'])
def get_statuses(request):
    tweets = api.search(q=request.data['search'], tweet_mode='extended')

    for tweet in tweets['statuses']:
        if 'retweeted_status' in tweet:
            tweet_text = tweet['retweeted_status']['full_text']
            tweet_id = tweet['retweeted_status']['id_str']
            tweet_created_at = tweet['retweeted_status']['created_at']
        else:
            tweet_text = tweet['full_text']
            tweet_id = tweet['id_str']
            tweet_created_at = tweet['created_at']

        serializer = TwitterDataSerializer(data={
            'status_id': tweet_id,
            'text': tweet_text,
            'retweet_count': tweet['retweet_count'],
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet_created_at,'%a %b %d %H:%M:%S +0000 %Y')),
            'user': {
                'user_id': tweet['user']['id_str'],
                'name': tweet['user']['name']
            }
        })
        
        if serializer.is_valid():
            try:
                temp = TwitterData.objects.get(status_id=tweet_id)
                temp['retweet_count'] = tweet['retweet_count']
                serializer = temp
            except TwitterData.DoesNotExist:
                pass
            serializer.save()
        else:
            return JsonResponse(serializer.errors, status=400, safe=False)

    serializer = TwitterDataSerializer(TwitterData.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)
