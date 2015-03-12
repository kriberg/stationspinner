from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.evemail.views import MailViewset, SearchLanguagesViewset, \
    MailStatusViewset

router = routers.DefaultRouter()
router.register(r'Mail', MailViewset, 'Mail')
router.register(r'Languages', SearchLanguagesViewset, 'Languages')
router.register(r'MailStatus', MailStatusViewset, 'MailStatus')

urlpatterns = [
    url(r'^', include(router.urls)),
]