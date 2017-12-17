import time
import re
from django.views.decorators.csrf import csrf_exempt
from twython import Twython
from django.http import JsonResponse
from rest_framework.decorators import api_view
from googletrans import Translator

from twitter_api.serializers import TwitterDataSerializer
from twitter_api.models import TwitterData
# Create your views here.

API_KEY = 'gmYLVJ21JFa0YB8zhIo71GJ9m'
API_SECRET = '3CB6gOeqqpYLQ1Y1rlkVbvriCQjdyg3pXfq3kSpdjIR9kToSxj'
TOKEN_KEY = '3365870121-PcBq6nthIQRWrcGwNRg1xUW5LGaOJ9CLd8262Ie'
TOCKET_SECRET_KEY = 'AVUuT3QGFPK6x5icab7aSdI9fjC0Cje2tkLVsnIhfX9yI'


api = Twython(API_KEY, API_SECRET, TOKEN_KEY, TOCKET_SECRET_KEY)


@api_view(['POST'])
def fetch_statuses(request):
    tweets = api.search(q=request.data['search'],
                        tweet_mode='extended',
                        since=request.data['since'],
                        until=request.data['until'],
                        count=request.data['count'])

    for tweet in tweets['statuses']:
        if 'retweeted_status' in tweet:
            tweet_text = tweet['retweeted_status']['full_text']
            tweet_id = tweet['retweeted_status']['id_str']
            created_at = tweet['retweeted_status']['created_at']
            retweeted_at = tweet['retweeted_status']['created_at']
        else:
            tweet_text = tweet['full_text']
            tweet_id = tweet['id_str']
            created_at = tweet['created_at']
            retweeted_at = None

        try:
            temp = TwitterData.objects.get(status_id=tweet_id)
            temp['retweet_count'] = tweet['retweet_count']
            serializer = temp
        except TwitterData.DoesNotExist:
            serializer = TwitterDataSerializer(data={
                'status_id': tweet_id,
                'text': tweet_text,
                'translated_text': translate_text(tweet_text),
                'retweet_count': tweet['retweet_count'],
                'created_at': format_date(created_at),
                'retweeted_at': format_date(retweeted_at),
                'user': {
                    'user_id': tweet['user']['id_str'],
                    'name': tweet['user']['name']
                }
            })

        if serializer.is_valid():
            serializer.save()
        else:
            return JsonResponse(serializer.errors, status=400, safe=False)

    serializer = TwitterDataSerializer(TwitterData.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)


def format_date(date):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(date,'%a %b %d %H:%M:%S +0000 %Y'))


def translate_text(text):
    translator = Translator()
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)

    sanitized_text = emoji_pattern.sub(r'', text)
    text = translator.translate(sanitized_text, dest='en').text

    return text

@csrf_exempt
def get_twitter_statuses_list(request):
    twitter_data = TwitterData.objects.all()
    serializer = TwitterDataSerializer(twitter_data, many=True)
    result = serializer.data

    return JsonResponse(result, safe=False)
