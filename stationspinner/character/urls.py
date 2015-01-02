from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.character.views import CharacterSheetViewset, \
    NotificationViewset, MailMessageViewset

router = routers.DefaultRouter()
router.register(r'CharacterSheet', CharacterSheetViewset)
router.register(r'Notifications', NotificationViewset)
router.register(r'MailMessage', MailMessageViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
]