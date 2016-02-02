from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.accounting.views import APIKeyViewset, LoginView, \
    CapsulerViewset, LogoutView, MissingTrainingViewset, RevalidateKeyView, \
    ObtainAuthTokenView, CheckAuthTokenView, RefreshAuthTokenView

router = routers.DefaultRouter()
router.register(r'capsuler', CapsulerViewset, 'capsuler')
router.register(r'missing-training', MissingTrainingViewset, 'missing-training')
router.register(r'apikeys', APIKeyViewset, 'apikeys')

urlpatterns = [
    url(r'^obtaintoken/$', ObtainAuthTokenView.as_view(), name='accounting_obtaintoken'),
    url(r'^checktoken/$', CheckAuthTokenView.as_view(), name='accounting_checktoken'),
    url(r'^refreshtoken/$', RefreshAuthTokenView.as_view(), name='accounting_refreshtoken'),
    url(r'^logout/$', LogoutView.as_view(), name='accounting_logout'),
    url(r'^login/$', LoginView.as_view(), name='accounting_login'),
    url(r'^revalidate-key/$', RevalidateKeyView.as_view(), name='accounting_revalidate_key'),
    url(r'^', include(router.urls)),
]