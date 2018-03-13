from django.conf.urls import url
from stock_data import views

urlpatterns = [
    url(r'^stock/fetch', views.fetch_stock_data),
    url(r'^stock/$', views.get_stock_list),
]