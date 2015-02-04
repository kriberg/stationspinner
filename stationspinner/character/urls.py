from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.character.views import CharacterSheetViewset, \
    NotificationViewset, MailMessageViewset, DistinctAllianceViewset, \
    DistinctCorporationViewset

router = routers.DefaultRouter()
router.register(r'CharacterSheet', CharacterSheetViewset)
router.register(r'Notifications', NotificationViewset)
router.register(r'MailMessage', MailMessageViewset)
router.register(r'DistinctCorporations', DistinctCorporationViewset)
router.register(r'DistinctAlliances', DistinctAllianceViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
]