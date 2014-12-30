from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.accounting.views import APIKeyViewset, \
    CapsulerViewset, LogoutView

router = routers.DefaultRouter()
router.register(r'capsuler', CapsulerViewset)
router.register(r'apikey', APIKeyViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^logout/$', LogoutView.as_view())
]