from django.conf.urls import url
from stationspinner.universe.views import ServerStatusView

urlpatterns = [
    url(r'^tranquility/$', ServerStatusView.as_view()),
]
