from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
from rest_framework.authtoken import views as authtoken
admin.autodiscover()

from stationspinner.settings import DEBUG

app_urls = [
    url(r'^char/', include('stationspinner.character.urls')),
    url(r'^corp/', include('stationspinner.corporation.urls')),
    url(r'^sde/', include('stationspinner.sde.urls')),
    url(r'^evemail/', include('stationspinner.evemail.urls')),
    url(r'^accounting/', include('stationspinner.accounting.urls')),
    url(r'^prices/', include('stationspinner.evecentral.urls')),
    url(r'^statistics/', include('stationspinner.statistics.urls')),
    url(r'^universe/', include('stationspinner.universe.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^auth/', authtoken.obtain_auth_token),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', RedirectView.as_view(url='/', permanent=True))
]

if DEBUG:
    urlpatterns = [url(r'^api/', include(app_urls))]
else:
    urlpatterns = app_urls
