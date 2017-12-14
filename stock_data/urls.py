from django.conf.urls import url
from stock_data import views

urlpatterns = [
    url(r'^stock/load$', views.load_stock_data),
    url(r'^stock/$', views.get_stock_list),
    url(r'^stock/(?P<pk>[0-9]+)/$', views.stock_item_detail),
]