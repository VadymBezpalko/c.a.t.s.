from textblob import TextBlob
from django.http import JsonResponse

from twitter_api.serializers import TwitterDataSerializer
from twitter_api.models import TwitterData


def make_sentiment_analysis(request):
    twitter_data = TwitterData.objects.all()

    for tweet in twitter_data:
        # print('-------------------')
        # print(tweet['text'])
        # print('analyzing tweet...')
        sentiment_analysis = TextBlob(tweet['translated_text'])
        # print(sentiment_analysis.sentiment)
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
