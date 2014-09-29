from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.character.views import CharacterSheetViewset

router = routers.DefaultRouter()
router.register(r'character_sheets', CharacterSheetViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
]