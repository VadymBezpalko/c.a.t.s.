import time
import re

import json
from django.views.decorators.csrf import csrf_exempt
import requests
from twython import Twython
from django.http import JsonResponse
from rest_framework.decorators import api_view
from googletrans import Translator
from textblob import TextBlob

from twitter_api.serializers import TwitterDataSerializer
from twitter_api.models import TwitterData

# Create your views here.

API_KEY = 'gmYLVJ21JFa0YB8zhIo71GJ9m'
API_SECRET = '3CB6gOeqqpYLQ1Y1rlkVbvriCQjdyg3pXfq3kSpdjIR9kToSxj'
TOKEN_KEY = '3365870121-PcBq6nthIQRWrcGwNRg1xUW5LGaOJ9CLd8262Ie'
TOCKET_SECRET_KEY = 'AVUuT3QGFPK6x5icab7aSdI9fjC0Cje2tkLVsnIhfX9yI'

api = Twython(API_KEY, API_SECRET)


@api_view(['POST'])
def fetch_statuses(request):
    count_of_tweets_to_be_fetched = int(request.data['count'])
    tweets_length = 0
    for i in range(0, int(count_of_tweets_to_be_fetched / 100) + 1):
        print(i, '******************************')
        if int(count_of_tweets_to_be_fetched) < tweets_length:
            break

        if i == 0:
            results = api.search(q=request.data['search'],
                                 tweet_mode='extended',
                                 since=request.data['since'],
                                 until=request.data['until'],
                                 count=100)
        else:
            # After the first call we should have max_id from result of previous call. Pass it in query.
            results = api.search(q=request.data['search'],
                                 tweet_mode='extended',
                                 count=100,
                                 since=request.data['since'],
                                 include_entities='true',
                                 max_id=next_max_id)

            # STEP 2: Save the returned tweets
        for tweet in results['statuses']:
            if int(count_of_tweets_to_be_fetched) < tweets_length:
                break
            print('-------------------')
            print(tweets_length)
            print(tweet['full_text'])
            print(tweet['created_at'])
            new_tweet = True
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
                if tweet['retweet_count'] > temp['retweet_count']:
                    serializer = TwitterDataSerializer(temp, data={"retweet_count": tweet["retweet_count"]})
                    new_tweet = False
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
            if new_tweet and serializer.is_valid():
                serializer.save()
                tweets_length += 1
            else:
                return JsonResponse(serializer.errors, status=400, safe=False)

            # STEP 3: Get the next max_id
        try:
            # Parse the data returned to get max_id to be passed in consequent call.
            next_results_url_params = results['search_metadata']['next_results']
            next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
        except:
            # No more next pages
            break

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
            data={'sentimental': {'comparative': tweet['sentimental_comparative'],
                                  'score': tweet['sentimental_score']}})
        if temp_serializer.is_valid():
            temp_serializer.save()

    return JsonResponse(TwitterDataSerializer(TwitterData.objects.all(), many=True).data, safe=False)


def analyze_tweets_nltk(request):
    twitter_data = TwitterData.objects.all()

    for tweet in twitter_data:
        print('-------------------')
        print(tweet['text'])
        print('analyzing tweet...')
        sentiment_analysis = TextBlob(tweet['translated_text'])
        print(sentiment_analysis.sentiment)
        temp_serializer = TwitterDataSerializer(
            tweet,
            data={
                'sentimental': {
                    'polarity': sentiment_analysis.sentiment.polarity,
                    'subjectivity': sentiment_analysis.sentiment.subjectivity
                }
            }
        )
        if temp_serializer.is_valid():
            temp_serializer.save()

    return JsonResponse(TwitterDataSerializer(TwitterData.objects.all(), many=True).data, safe=False)


def translate_tweets_nltk(request):
    twitter_data = TwitterData.objects.all()

    for tweet in twitter_data:
        print('-------------------')
        print(tweet['text'])
        if tweet['translated_text'] is None:
            print('translating tweet...')
            translated = TextBlob(tweet['text']).translate(to='en')
            print(translated)
            temp_serializer = TwitterDataSerializer(tweet, data={'translated_text': translated})
            if temp_serializer.is_valid():
                temp_serializer.save()
        else:
            print('tweet already been translated')

    return JsonResponse(TwitterDataSerializer(TwitterData.objects.all(), many=True).data, safe=False)
