from django.http import JsonResponse
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from rest_framework.decorators import api_view

from twitter_api.models import TwitterData
from named_entity.serializers import NamedEntityDataSerializer
from named_entity.models import NamedEntityData


@api_view(['GET'])
def named_entity_recognition(request):
    print(request.GET.get('search_term', None))
    twitter_data = TwitterData.objects(search_term=request.GET.get('search_term', None))

    for tweet in twitter_data:
        sentiment = tweet['sentimental']['polarity']
        entities = get_continuous_chunks(tweet['translated_text'])
        for entity in entities:
            temp_entity = entity.lower()
            try:
                temp = NamedEntityData.objects.get(text=temp_entity)

                if sentiment >= 0:
                    serializer = NamedEntityDataSerializer(temp, data={"pos_quantity": temp['pos_quantity'] + 1})
                else:
                    serializer = NamedEntityDataSerializer(temp, data={"neg_quantity": temp['neg_quantity'] + 1})

            except NamedEntityData.DoesNotExist:
                serializer = NamedEntityDataSerializer(data={
                    'text': temp_entity,
                    'pos_quantity': 1 if sentiment >= 0 else 0,
                    'neg_quantity': 1 if sentiment < 0 else 0
                })

            if serializer.is_valid():
                serializer.save()
            else:
                return JsonResponse(serializer.errors, status=400, safe=False)

    return JsonResponse(NamedEntityDataSerializer(NamedEntityData.objects.all(), many=True).data, safe=False)


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
