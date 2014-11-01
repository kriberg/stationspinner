from stationspinner.celery import app
from celery import group
from stationspinner.evecentral.models import Market, MarketItem
from stationspinner.libs.pragma import get_location_name
from stationspinner.sde.models import InvType
from evelink.thirdparty.eve_central import EVECentral
from urllib2 import urlopen
from datetime import datetime, timedelta
from pytz import UTC
from django.db.models import Q
from celery.utils.log import get_task_logger
from traceback import format_exc

log = get_task_logger(__name__)


def _market_items():
    market_items = InvType.objects.filter(published=True,
                                          marketGroupID__lt=35000)
    typeIDs = [i.pk for i in market_items.order_by('id')]

    for i in xrange(0, len(typeIDs), 100):
        yield typeIDs[i:i+100]


@app.task(name='evecentral.update_all_markets')
def update_all_markets():
    market_updates = []
    six_hours_ago = datetime.now(tz=UTC) - timedelta(hours=6)
    for market in Market.objects.filter(
                    Q(last_updated__lt=six_hours_ago) | Q(last_updated=None)):
        market_updates.extend(update_market(market.locationID))
        market.updated()
        log.info('Updating "{0}" market'.format(get_location_name(market.locationID)))
    group(market_updates).apply_async()


def update_market(locationID):
    tasks = []
    for typeIDs in _market_items():
        tasks.append(parse_market_data.s(typeIDs, locationID))
    return tasks

@app.task(name='evecentral.parse_market_data')
def parse_market_data(typeIDs, locationID):
    ec = EVECentral(url_fetch_func=lambda url: urlopen(url).read())
    try:
        if locationID > 30000000:
            data = ec.market_stats(type_ids=typeIDs, system=locationID)
        else:
            data = ec.market_stats(type_ids=typeIDs, region=locationID)
    except Exception, ex:
        log.error('Could not update locationID {0}: {1}'.format(locationID,
                                                                format_exc(ex)))
        return

    for typeID, price_data in data.items():
        prices = {}
        for price_type in ('buy', 'sell'):
            type_data = price_data[price_type]
            for statistic, value in type_data.items():
                prices['{0}_{1}'.format(price_type, statistic)] = value
        MarketItem.objects.update_or_create(typeID=typeID,
                                            locationID=locationID,
                                            defaults=prices)





