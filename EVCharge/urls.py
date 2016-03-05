from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^ev/(?P<car_id>[0-9 A-Z a-z]+)$', views.ev, name='ev'),
  url(r'^processing$', views.processing, name='processing'),
  url(r'^ev/(?P<car_id>[0-9 A-Z a-z]+)/(?P<user_id>[0-9]+)/charging/(?P<duration>[0-9 .]+)/(?P<distance>[0-9 .]+)$', views.charging, name='charging'),
]