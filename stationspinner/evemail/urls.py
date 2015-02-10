from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.evemail.views import MailViewset, SearchLanguagesViewset, \
    MailStatusViewset

router = routers.DefaultRouter()
router.register(r'Mail', MailViewset)
router.register(r'Languages', SearchLanguagesViewset, base_name='evemail_languages')
router.register(r'MailStatus', MailStatusViewset, base_name='mail_status')

urlpatterns = [
    url(r'^', include(router.urls)),
]