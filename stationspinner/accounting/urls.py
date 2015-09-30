from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.accounting.views import APIKeyViewset, \
    CapsulerViewset, LogoutView, MissingTrainingViewset, RevalidateKeyView

router = routers.DefaultRouter()
router.register(r'capsuler', CapsulerViewset, 'capsuler')
router.register(r'missing-training', MissingTrainingViewset, 'missing-training')
router.register(r'apikeys', APIKeyViewset, 'apikeys')

urlpatterns = [
    url(r'^logout/$', LogoutView.as_view(), name='accounting_logout'),
    url(r'^revalidate-key/$', RevalidateKeyView.as_view(), name='accounting_revalidate_key'),
    url(r'^', include(router.urls)),
]