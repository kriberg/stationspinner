from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.contrib import admin
from rest_framework.authtoken import views as authtoken
admin.autodiscover()

from stationspinner.settings import DEBUG

if DEBUG:
    urlpatterns = patterns('',
        url(r'^api/', include([
            url(r'^char/', include('stationspinner.character.urls')),
            url(r'^corp/', include('stationspinner.corporation.urls')),
            url(r'^sde/', include('stationspinner.sde.urls')),
            url(r'^evemail/', include('stationspinner.evemail.urls')),
            url(r'^accounting/', include('stationspinner.accounting.urls')),
            url(r'^prices/', include('stationspinner.evecentral.urls')),
            url(r'^universe/', include('stationspinner.universe.urls')),
            url(r'^registration/', include('registration.backends.default.urls')),
            url(r'^grappelli/', include('grappelli.urls')),
            url(r'^auth/', authtoken.obtain_auth_token),
            url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
            url(r'^admin/', include(admin.site.urls)),
            url(r'^$', RedirectView.as_view(url='/', permanent=True))
            ]))
    )
else:
    urlpatterns = patterns('',
        url(r'^char/', include('stationspinner.character.urls')),
        url(r'^corp/', include('stationspinner.corporation.urls')),
        url(r'^sde/', include('stationspinner.sde.urls')),
        url(r'^evemail/', include('stationspinner.evemail.urls')),
        url(r'^accounting/', include('stationspinner.accounting.urls')),
        url(r'^prices/', include('stationspinner.evecentral.urls')),
        url(r'^universe/', include('stationspinner.universe.urls')),
        url(r'^registration/', include('registration.backends.default.urls')),
        url(r'^grappelli/', include('grappelli.urls')),
        url(r'^auth/', authtoken.obtain_auth_token),
        url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
        url(r'^admin/', include(admin.site.urls)),
        url(r'^$', RedirectView.as_view(url='/', permanent=True))
    )
