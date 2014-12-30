from django.conf.urls import patterns, url
from stationspinner.universe.views import ServerStatusView

urlpatterns = patterns('',
    url(r'^tranquility/$', ServerStatusView.as_view()),
    )