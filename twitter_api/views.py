import twitter
from django.http import HttpResponse, JsonResponse
# Create your views here.
from rest_framework.decorators import api_view

api = twitter.Api(consumer_key='gmYLVJ21JFa0YB8zhIo71GJ9m',
                  consumer_secret='3CB6gOeqqpYLQ1Y1rlkVbvriCQjdyg3pXfq3kSpdjIR9kToSxj',
                  access_token_key='3365870121-PcBq6nthIQRWrcGwNRg1xUW5LGaOJ9CLd8262Ie',
                  access_token_secret='AVUuT3QGFPK6x5icab7aSdI9fjC0Cje2tkLVsnIhfX9yI')


@api_view(['POST'])
def get_statuses(request):
    results = api.GetSearch(term=request.data['search'],)
    # since=request.data['since'],
    # until=request.data['until'])
    print(results)

    return HttpResponse(status=200)
