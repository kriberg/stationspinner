from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.evemail.views import MailViewset, SearchLanguagesViewset

router = routers.DefaultRouter()
router.register(r'Mail', MailViewset)
router.register(r'Languages', SearchLanguagesViewset, base_name='evemail_Languages')

urlpatterns = [
    url(r'^', include(router.urls)),
]