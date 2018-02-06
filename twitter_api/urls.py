from django.conf.urls import url
from twitter_api.views import fetcher
from twitter_api.views import translator
from twitter_api.views import analyzer

urlpatterns = [
    url(r'^twitter/fetch$', fetcher.fetch_statuses),
    url(r'^twitter/get$', fetcher.get_statuses),
    url(r'^twitter/translate$', translator.translate_tweets),
    url(r'^twitter/translate_nltk$', translator.translate_tweets),
    url(r'^twitter/analyze_nltk$', analyzer.analyze_tweets_nltk),
    url(r'^twitter/entity_extraction$', analyzer.named_entity_recognition),
    url(r'^twitter/$', fetcher.get_statuses_from_db),
]
