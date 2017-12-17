from django.conf.urls import url
from twitter_api import views

urlpatterns = [
    url(r'^twitter/fetch', views.fetch_statuses),
    url(r'^twitter/get', views.get_statuses),
    url(r'^twitter/translate', views.translate_tweets),
    url(r'^twitter/$', views.get_twitter_statuses_list),
]
