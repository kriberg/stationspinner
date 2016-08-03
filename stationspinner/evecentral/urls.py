from django.conf.urls import url
from stationspinner.evecentral.views import PriceView

urlpatterns = [
    url(r'^(?P<locationID>\d+)/$', PriceView.as_view()),
]
