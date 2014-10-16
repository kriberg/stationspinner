from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.character.views import CharacterSheetViewset, \
    AssetListViewset

router = routers.DefaultRouter()
router.register(r'CharacterSheet', CharacterSheetViewset)
router.register(r'AssetList', AssetListViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
]