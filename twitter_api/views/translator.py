import re
from django.http import JsonResponse
from googletrans import Translator
from textblob import TextBlob

from twitter_api.serializers import TwitterDataSerializer
from twitter_api.models import TwitterData


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
