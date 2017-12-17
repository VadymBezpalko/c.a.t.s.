import time
import re

import json
from django.views.decorators.csrf import csrf_exempt
import requests
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
        print('-------------------')
        print(tweet['full_text'])
        if 'retweeted_status' in tweet:
            print('retweeted')
            tweet_text = tweet['retweeted_status']['full_text']
            tweet_id = tweet['retweeted_status']['id_str']
            created_at = tweet['retweeted_status']['created_at']
            retweeted_at = tweet['created_at']
        else:
            print('original tweet')
            tweet_text = tweet['full_text']
            tweet_id = tweet['id_str']
            created_at = tweet['created_at']
            retweeted_at = None

        try:
            temp = TwitterData.objects.get(status_id=tweet_id)
            serializer = TwitterDataSerializer(temp, data={"retweet_count": tweet["retweet_count"]})
            print(temp)
            print('juz jest taki tweet')

        except TwitterData.DoesNotExist:
            print('tworzę nowy tweet')
            serializer = TwitterDataSerializer(data={
                'status_id': tweet_id,
                'text': tweet_text,
                # 'translated_text': translate_text(tweet_text),
                'retweet_count': tweet['retweet_count'],
                'created_at': format_date(created_at),
                'retweeted_at': format_date(retweeted_at) if retweeted_at is not None else None,
                'user': {
                    'user_id': tweet['user']['id_str'],
                    'name': tweet['user']['name']
                }
            })
        print(type(serializer))
        if serializer.is_valid():
            serializer.save()
        else:
            return JsonResponse(serializer.errors, status=400, safe=False)

    serializer = TwitterDataSerializer(TwitterData.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
def get_statuses(request):
    tweets = api.search(q=request.data['search'],
                        tweet_mode='extended',
                        since=request.data['since'],
                        until=request.data['until'],
                        count=request.data['count'])

    return JsonResponse(tweets)


def format_date(date):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(date, '%a %b %d %H:%M:%S +0000 %Y'))


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


def translate_tweets(request):
    twitter_data = TwitterData.objects.all()

    for tweet in twitter_data:
        print('-------------------')
        print(tweet['text'])
        if tweet['translated_text'] is None:
            print('translating tweet...')
            translated = translate_text(tweet['text'])
            print(translated)
            temp_serializer = TwitterDataSerializer(tweet, data={'translated_text': translated})
            if temp_serializer.is_valid():
                temp_serializer.save()
        else:
            print('tweet already been translated')

    return JsonResponse(TwitterDataSerializer(TwitterData.objects.all(), many=True).data, safe=False)


def analyze_tweets(request):
    try:
        analyzed = requests.post('http://localhost:3000/analyze/', data={
            'tweets': json.dumps(TwitterDataSerializer(TwitterData.objects.all(), many=True).data)
        })
    except ValueError as err:
        return JsonResponse(err.args, status=400, safe=False)
    analyzed = json.loads(analyzed.content.decode('utf-8', 'ignore'))

    for tweet in analyzed['result']:
        print('-------------------')
        print(tweet)
        temp_serializer = TwitterDataSerializer(TwitterData.objects.get(
            status_id=tweet['status_id']),
            data={'sentimental_comparative': tweet['sentimental_comparative'],
                  'sentimental_score': tweet['sentimental_score']})
        if temp_serializer.is_valid():
            temp_serializer.save()

    return JsonResponse(TwitterDataSerializer(TwitterData.objects.all(), many=True).data, safe=False)
