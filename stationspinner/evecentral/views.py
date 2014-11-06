from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.shortcuts import get_object_or_404, render
from django.core.cache import cache
from django.http import HttpResponse
from datetime import datetime
from pytz import UTC
from stationspinner.evecentral.models import Market, MarketItem
from stationspinner.libs.pragma import get_location_name


class PriceView(TemplateResponseMixin, View):
    template_name = 'evecentral/prices_list.html'

    def get(self, request, locationID):
        market = get_object_or_404(Market, locationID=locationID)
        key = hash(('prices_list', locationID))
        content = cache.get(key, None)

        if not content:
            print 'generated'
            prices = MarketItem.objects.filter(locationID=locationID).order_by('typeName')
            response = render(request, self.template_name, dictionary={
                'cached_until': market.cached_until,
                'name': get_location_name(market.locationID),
                'prices': prices,
            })
            cacheTimeSeconds = (market.cached_until - datetime.now(tz=UTC)).total_seconds()
            print cacheTimeSeconds
            cache.set(key, response.content, timeout=cacheTimeSeconds)
            return response
        else:
            print 'cached'
            return HttpResponse(content=content)