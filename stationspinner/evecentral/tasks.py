from stationspinner.celery import app
from celery import chord
from stationspinner.evecentral.models import Market, MarketItem
from stationspinner.libs.pragma import get_location_name
from stationspinner.sde.models import InvType
from stationspinner.settings import STATIC_ROOT
from evelink.thirdparty.eve_central import EVECentral
from urllib2 import urlopen
from datetime import datetime
from pytz import UTC
from django.db.models import Q
from celery.utils.log import get_task_logger
from traceback import format_exc
from os.path import join
import csv

log = get_task_logger(__name__)


def _market_items():
    market_items = InvType.objects.filter(published=True,
                                          marketGroupID__lt=35000)
    typeIDs = [i.pk for i in market_items.order_by('id')]

    for i in xrange(0, len(typeIDs), 100):
        yield typeIDs[i:i+100]

@app.task(name='evecentral.write_static_prices')
def write_static_prices():
    for market in Market.objects.all():
        market_items = MarketItem.objects.filter(locationID=market.locationID).order_by('typeName')
        with open(join(STATIC_ROOT, '{0}.csv'.format(market.locationID)), 'wb') as output:
            csvprices = csv.writer(output, delimiter=';')
            for item in market_items:
                try:
                    csvprices.writerow((item.typeID,
                                       item.typeName,
                                       item.buy_max,
                                       item.buy_min,
                                       item.buy_percentile,
                                       item.buy_volume,
                                       item.sell_max,
                                       item.sell_min,
                                       item.sell_percentile,
                                       item.sell_volume))
                except:
                    log.debug('Failed to render csv row for {0} at {1}.'.format(item, market.locationID))



@app.task(name='evecentral.update_all_markets')
def update_all_markets():
    market_updates = []
    for market in Market.objects.filter(
                    Q(cached_until__lte=datetime.now(tz=UTC)) | Q(cached_until=None)):
        market_updates.extend(update_market(market.locationID))
        market.updated()
        log.info('Updating "{0}" market'.format(get_location_name(market.locationID)))
    chord(market_updates, write_static_prices.s()).apply_async()


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
            data = ec.market_stats(type_ids=typeIDs, regions=locationID)
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
                                            typeName=InvType.objects.get(pk=typeID).typeName,
                                            defaults=prices)





