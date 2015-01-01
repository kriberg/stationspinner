from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.accounting.views import APIKeyViewset, \
    CapsulerViewset, LogoutView, AccountTrainingViewset

router = routers.DefaultRouter()
router.register(r'capsuler', CapsulerViewset)
router.register(r'apikey', APIKeyViewset)
router.register(r'account-training', AccountTrainingViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^logout/$', LogoutView.as_view())
]