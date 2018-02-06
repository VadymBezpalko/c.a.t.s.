from textblob import TextBlob
from django.http import JsonResponse

from twitter_api.serializers import TwitterDataSerializer
from twitter_api.models import TwitterData

from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree


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


def named_entity_recognition(request):
    twitter_data = TwitterData.objects.all()

    for tweet in twitter_data:
        print('-------------------')
        print(tweet['translated_text'])
        print('extracting NE tweet...')
        entities = get_continuous_chunks(tweet['translated_text'])
        print(entities)
        temp_serializer = TwitterDataSerializer(
            tweet,
            data={
                'entities': entities
            }
        )
        if temp_serializer.is_valid():
            temp_serializer.save()

    return JsonResponse(TwitterDataSerializer(TwitterData.objects.all(), many=True).data, safe=False)


def get_continuous_chunks(text):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
            if type(i) == Tree:
                    current_chunk.append(" ".join([token for token, pos in i.leaves()]))
            elif current_chunk:
                    named_entity = " ".join(current_chunk)
                    if named_entity not in continuous_chunk:
                            continuous_chunk.append(named_entity)
                            current_chunk = []
            else:
                    continue
    return continuous_chunk
