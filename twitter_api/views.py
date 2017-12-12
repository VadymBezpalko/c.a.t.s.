from twitter_api.models import User
from twython import Twython
from django.http import HttpResponse, JsonResponse
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
    # results = api.GetSearch(term=request.data['search'], result_type='mixed')
    # since=request.data['since'],
    # until=request.data['until'])
    results = api.search(q=request.data['search'])
    print(results)
    for row in results['statuses']:
        serializer = TwitterDataSerializer(data={
            'status_id': row['id_str'],
            'text': row['text'],
            'retweet_count': row['retweet_count'],
            'created_at': row['created_at'],
            'user': {
                'user_id': row['user']['id_str'],
                'name': row['user']['name']
            }
        })
        if serializer.is_valid():
            serializer.save()
        else:
            return JsonResponse(serializer.errors, status=400, safe=False)

    serializer = TwitterDataSerializer(TwitterData.objects.all(), many=True)

    return JsonResponse(serializer.data, safe=False)
