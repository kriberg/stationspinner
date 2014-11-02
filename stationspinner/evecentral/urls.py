from django.conf.urls import patterns, url
from stationspinner.evecentral.views import PriceView

urlpatterns = patterns('',
    url(r'^(?P<locationID>\d+)/$', PriceView.as_view()),
    )