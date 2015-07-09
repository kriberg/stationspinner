from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.sde.views import InvTypeViewset

router = routers.DefaultRouter()
router.register(r'InvType', InvTypeViewset, 'InvType')

urlpatterns = [
    url(r'^', include(router.urls)),
]