from django.conf.urls import url
from twitter_api import views

urlpatterns = [
    url(r'^twitter/fetch', views.fetch_statuses),
]
