from django.conf.urls import url
from twitter_api import views

urlpatterns = [
    url(r'^twitter/search$', views.get_statuses),
]
