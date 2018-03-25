from django.conf.urls import url
from named_entity import views

urlpatterns = [
    url(r'^named_entity/process$', views.named_entity_recognition),
]