from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.sde.views import InvTypeViewset, InvMarketGroupView

router = routers.DefaultRouter()
router.register(r'InvType', InvTypeViewset, 'InvType')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^InvMarketGroups/', InvMarketGroupView.as_view(), name='InvMarketGroups')
]