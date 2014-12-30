from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.corporation.views import CorporationSheetViewset

router = routers.DefaultRouter()
router.register(r'CorporationSheet', CorporationSheetViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
]