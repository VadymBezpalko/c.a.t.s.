from django.conf.urls import url
from twitter_api.views import fetcher, correlation_analysis
from twitter_api.views import translator
from twitter_api.views import sentiment_analyzer

urlpatterns = [
    url(r'^twitter/fetch$', fetcher.fetch_statuses),
    url(r'^twitter/translate$', translator.translate_tweets),
    url(r'^twitter/translate_nltk$', translator.translate_tweets),
    url(r'^twitter/analyze_nltk$', sentiment_analyzer.analyze_tweets_nltk),
    url(r'^twitter/entity_extraction$', sentiment_analyzer.named_entity_recognition),
    url(r'^twitter/correlation$', correlation_analysis.get_pearson_correlation),
    url(r'^twitter/$', fetcher.get_processed_messages),
]
