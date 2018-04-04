
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from django.http import JsonResponse
from twython import Twython
from django.conf import settings
from twitter_api.serializers import TwitterDataSerializer
from twitter_api.models import TwitterData
import common.util as util


api = Twython(settings.API_KEY, settings.API_SECRET)


@api_view(['POST'])
def fetch_statuses(request):
    count_of_tweets_to_be_fetched = int(request.data['count'])
    tweets_length = 0
    for i in range(0, int(count_of_tweets_to_be_fetched / 100) + 1):
        # print(i, '******************************')
        if int(count_of_tweets_to_be_fetched) < tweets_length:
            break

        if i == 0:
            results = api.search(q=request.data['search'],
                                 tweet_mode='extended',
                                 # since=(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                                 since=request.data['since'],
                                 until=request.data['until'],
                                 # until=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                                 count=100)
        else:
            # After the first call we should have max_id from result of previous call. Pass it in query.
            results = api.search(q=request.data['search'],
                                 tweet_mode='extended',
                                 count=100,
                                 # since=(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                                 since=request.data['since'],
                                 include_entities='true',
                                 max_id=next_max_id)

            # STEP 2: Save the returned tweets
        for tweet in results['statuses']:
            if int(count_of_tweets_to_be_fetched) < tweets_length:
                break
            # print('-------------------')
            # print(tweets_length)
            # print(tweet['full_text'])
            # print(tweet['created_at'])
            if 'retweeted_status' in tweet:
                # print('retweeted')
                tweet_text = tweet['retweeted_status']['full_text']
                tweet_id = tweet['retweeted_status']['id_str']
                created_at = tweet['retweeted_status']['created_at']
                retweeted_at = tweet['created_at']
            else:
                # print('original tweet')
                tweet_text = tweet['full_text']
                tweet_id = tweet['id_str']
                created_at = tweet['created_at']
                retweeted_at = None

            try:
                temp = TwitterData.objects.get(status_id=tweet_id)
                # print('juz jest taki tweet')
                if tweet['retweet_count'] > temp['retweet_count']:
                    serializer = TwitterDataSerializer(temp, data={"retweet_count": tweet["retweet_count"]})
                else:
                    continue

            except TwitterData.DoesNotExist:
                # print('tworzę nowy tweet')
                serializer = TwitterDataSerializer(data={
                    'status_id': tweet_id,
                    'text': tweet_text,
                    'search_term': request.data['search'],
                    # 'translated_text': translate_text(tweet_text),
                    'retweet_count': tweet['retweet_count'],
                    'created_at': util.format_date(created_at),
                    'retweeted_at': util.format_date(retweeted_at) if retweeted_at is not None else None,
                    'user': {
                        'user_id': tweet['user']['id_str'],
                        'name': tweet['user']['name']
                    }
                })
            if serializer.is_valid():
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
def get_direct_statuses(request):  # for debug purposes
    tweets = api.search(q=request.data['search'],
                        tweet_mode='extended',
                        since=request.data['since'],
                        until=request.data['until'],
                        count=request.data['count'])

    return JsonResponse(tweets)


@api_view(['GET'])
def get_processed_messages(request):
    search_term = request.GET.get('search_term', None)

    if search_term is not None:
        twitter_query = TwitterData.objects(
            search_term=search_term,
            created_at__gte=request.GET.get('from', None),
            created_at__lte=request.GET.get('to', None)
        )
    else:
        twitter_query = TwitterData.objects.all()

    twitter_messages = util.get_serialized_data(twitter_query.order_by('created_at'), 'twitter')
    result = util.summarize_twitter_data_by_day(twitter_messages)

    return JsonResponse(result, safe=False)



