from django.conf.urls import url
from named_entity import views

urlpatterns = [
    url(r'^named_entity/$', views.get_ner_data),
    url(r'^named_entity/process$', views.ner_process),
]