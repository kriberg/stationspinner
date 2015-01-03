from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.accounting.views import APIKeyViewset, \
    CapsulerViewset, LogoutView, MissingTrainingViewset

router = routers.DefaultRouter()
router.register(r'capsuler', CapsulerViewset)
router.register(r'missing-training', MissingTrainingViewset)
router.register(r'apikeys', APIKeyViewset)

urlpatterns = [
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^', include(router.urls)),
]