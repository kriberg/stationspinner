from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.character.views import CharacterSheetViewset, \
    NotificationViewset

router = routers.DefaultRouter()
router.register(r'CharacterSheet', CharacterSheetViewset)
router.register(r'Notifications', NotificationViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
]