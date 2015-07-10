from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.corporation.views import CorporationSheetViewset, \
    AssetLocationsView

router = routers.DefaultRouter()
router.register(r'CorporationSheet', CorporationSheetViewset, 'CorporationSheet')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^AssetLocations', AssetLocationsView.as_view(), name='corporation_asset_locations')
]