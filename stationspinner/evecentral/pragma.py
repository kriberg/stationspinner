from django.core.cache import cache
from stationspinner.evecentral.models import MarketItem
from stationspinner.settings import DEFAULT_MARKET
from stationspinner.libs.pragma import get_location_id

MARKET_ID = get_location_id(DEFAULT_MARKET)

def get_item_market_value(typeID):
    value = cache.get(hash((MARKET_ID, typeID)))
    if not value:
        try:
            item = MarketItem.objects.get(typeID=typeID,
                            locationID=MARKET_ID)
            value = item.sell_percentile
        except MarketItem.DoesNotExist:
            # The item doesnt exist. We want to cache this regardless, so we
            # don't have to keep looking up unknown items
            value = 0.0

        cache.set(hash((MARKET_ID, typeID)), value)

    return value