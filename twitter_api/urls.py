from django.conf.urls import url
from twitter_api.views import fetcher, correlation_analysis
from twitter_api.views import translator
from twitter_api.views import sentiment_analyzer

urlpatterns = [
    url(r'^twitter/fetch$', fetcher.fetch_statuses),
    url(r'^twitter/translate$', translator.translate_tweets),
    url(r'^twitter/sentiment_analysis', sentiment_analyzer.make_sentiment_analysis),
    url(r'^twitter/correlation$', correlation_analysis.get_pearson_correlation),
    url(r'^twitter/debug', fetcher.get_direct_statuses),
    url(r'^twitter/processed_messages$', fetcher.get_processed_messages),
    url(r'^twitter/messages$', fetcher.get_twitter_messages),
]
