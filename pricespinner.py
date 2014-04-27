import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from threading import Thread
import logging
import sys
import ConfigParser
import urllib2
import json
import Queue
from evelink.thirdparty.eve_central import EVECentral
from traceback import format_exc

MARKET_ITEMS = 'SELECT typeid FROM invtypes WHERE published=1 AND marketgroupid IS NOT NULL AND marketgroupid != 350001'
CREST_URL = 'http://public-crest.eveonline.com/market/%s/types/%s/history/'

class PriceSpinner():
    BLOCK_SIZE = 100
    hqueue = Queue.Queue()
    dqueue = Queue.Queue()
    def __init__(self, configfile):
        self.config = ConfigParser.SafeConfigParser()
        self.config.readfp(open(configfile))
        self.log = logging.getLogger('pricespinner')
        handler = logging.FileHandler(self.config.get('pricespinner', 'log'))
        formatter = logging.Formatter('%(asctime)s %(thread)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)
        self.hthreads = int(self.config.get('pricespinner', 'history_threads'))
        self.dthreads = int(self.config.get('pricespinner', 'data_threads'))

        db_params = self.config.items('database')
        conn_string = ' '.join(map(lambda a: '%s=%s' % (a[0], a[1]), db_params))
        self.conn = psycopg2.connect(conn_string)
        self.conn.autocommit = True
        self.pool = ThreadedConnectionPool(self.hthreads+self.dthreads, 100, conn_string)
        self.ec = EVECentral()
    def cursor(self):
        return self.conn.cursor()

    def get_system_ids(self):
        system_names = map(lambda a: a.strip(), self.config.get('pricespinner', 'systems').split(','))
        cur = self.cursor()
        cur.execute('SELECT itemid, itemname FROM mapdenormalize WHERE itemname IN %s', (tuple(system_names),))
        res = cur.fetchall()
        return res

    def get_region_ids(self):
        region_names = map(lambda a: a.strip(), self.config.get('pricespinner', 'regions').split(','))
        cur = self.cursor()
        cur.execute('SELECT itemid, itemname FROM mapdenormalize WHERE itemname IN %s', (tuple(region_names),))
        res = cur.fetchall()
        return res

    def get_items(self):
        cur = self.cursor()
        cur.execute(MARKET_ITEMS)
        res = cur.fetchall()
        typeids = map(lambda t: t[0], res)
        return typeids

    def fill_crest_queue(self):
        url = 'http://public-crest.eveonline.com/market/%s/types/%s/history/'
        regions = self.get_region_ids()
        items = self.get_items()

        for regionid, regionname in regions:
            for typeid in items:
                self.hqueue.put((regionid, typeid))

    def fill_evecentral_queue(self):
        with self.cursor() as cur:
            cur.execute(MARKET_ITEMS)
            systems = self.get_system_ids()

            block = cur.fetchmany(size=self.BLOCK_SIZE)
            while block:
                typeids = map(lambda t: t[0], block)
                for system in systems:
                    self.dqueue.put((system, typeids))
                block = cur.fetchmany(size=self.BLOCK_SIZE)

    def refresh_crest_history(self):
        with self.cursor() as cur:
            cur.execute('SELECT MAX(timestamp) FROM markethistory')
            res = cur.fetchone()[0]
            print res
        for i in range(self.hthreads):
            t = Thread(target=self.crest_worker)
            t.daemon = True
            t.start()
        self.fill_crest_queue()
        self.log.info('Fetching %s crest market histories' % self.hqueue.qsize())
        self.hqueue.join()

    def refresh_evecentral_prices(self):
        self.log.info('Fetching eve central prices')
        for i in range(self.dthreads):
            t = Thread(target=self.evecentral_worker)
            t.daemon = True
            t.start()
        self.fill_evecentral_queue()
        self.dqueue.join()

    def crest_worker(self):
        conn = self.pool.getconn()
        conn.autocommit = True
        with conn.cursor() as cur:
            while True:
                regionid, typeid = self.hqueue.get()
                try:
                    req = urllib2.urlopen(CREST_URL % (regionid, typeid))
                    type_history = json.load(req)
                    req.close()
                except Exception, ex:
                    self.log.error('Region: %s, Type: %s Error:\n%s' % (regionid, typeid, format_exc(ex)))
                    continue
                history_data = []
                for marketdata in type_history['items']:
                    marketdata['locationid'] = regionid
                    marketdata['typeid'] = typeid
                    marketdata['volume'] = int(marketdata['volume_str'])
                    marketdata['orderCount'] = int(marketdata['orderCount_str'])
                    marketdata.pop('volume_str')
                    marketdata.pop('orderCount_str')
                    history_data.append(marketdata)
                cur.executemany('''
                    WITH upsert AS (UPDATE markethistory SET
                        timestamp=%(date)s,
                        typeid=%(typeid)s,
                        locationid=%(locationid)s,
                        volume=%(volume)s,
                        orders=%(orderCount)s,
                        low=%(lowPrice)s,
                        high=%(highPrice)s,
                        avg=%(avgPrice)s
                    WHERE typeid=%(typeid)s AND locationid = %(locationid)s AND timestamp=%(date)s RETURNING *)
                    INSERT INTO markethistory (
                        timestamp, typeid, locationid, volume, orders, low, high, avg)
                    SELECT
                        %(date)s, %(typeid)s, %(locationid)s, %(volume)s,
                        %(orderCount)s, %(lowPrice)s, %(highPrice)s, %(avgPrice)s
                    WHERE NOT EXISTS (SELECT * FROM upsert)''', tuple(history_data))
                self.log.debug('Item %s, region %s done.' % (typeid, regionid))
                self.hqueue.task_done()

    def evecentral_worker(self):
        conn = self.pool.getconn()
        conn.autocommit = True
        with conn.cursor() as cur:
            while True:
                system, typeids = self.dqueue.get()
                try:
                    prices = self.ec.market_stats(typeids, system=system[0])
                except Exception, ex:
                    self.log.error('System: %s Error:\n%sTypes:\n%s' % (system[1], format_exc(ex), typeids))
                    continue
                # 22: {'all': {'avg': 2866.75,
                #         'max': 5110.1,
                #         'median': 3180.31,
                #         'min': 1265.0,
                #         'percentile': 1683.28,
                #         'stddev': 705.11,
                #         'volume': 818746},
                #     'buy': {'avg': 2749.09,
                #         'max': 3191.07,
                #         'median': 3113.77,
                #         'min': 1265.0,
                #         'percentile': 3190.69,
                #         'stddev': 722.74,
                #         'volume': 689444},
                #     'id': 22,
                #     'sell': {'avg': 3494.12,
                #         'max': 5110.1,
                #         'median': 3472.87,
                #         'min': 3379.9,
                #         'percentile': 3390.52,
                #         'stddev': 429.8,
                #         'volume': 129302}},
                price_data = []
                for typeid in prices.keys():
                    price = prices[typeid]
                    type_data = {'typeid': typeid, 'locationid': system[0]}
                    for order_type in ('buy', 'sell'):
                        for figure, value in price[order_type].items():
                            type_data['%s_%s' % (order_type, figure)] = value
                    price_data.append(type_data)

                cur.executemany('''
                    WITH upsert AS (UPDATE marketdata SET
                        timestamp=current_timestamp,
                        buy_volume=%(buy_volume)s,
                        buy_avg=%(buy_avg)s,
                        buy_max=%(buy_max)s,
                        buy_min=%(buy_min)s,
                        buy_stddev=%(buy_stddev)s,
                        buy_median=%(buy_median)s,
                        buy_percentile=%(buy_percentile)s,
                        sell_volume=%(sell_volume)s,
                        sell_avg=%(sell_avg)s,
                        sell_max=%(sell_max)s,
                        sell_min=%(sell_min)s,
                        sell_stddev=%(sell_stddev)s,
                        sell_median=%(sell_median)s,
                        sell_percentile=%(sell_percentile)s
                    WHERE typeid=%(typeid)s AND locationid = %(locationid)s RETURNING *)
                    INSERT INTO marketdata (
                        typeid, locationid, timestamp, buy_volume, buy_avg,
                        buy_max, buy_min, buy_stddev, buy_median,
                        buy_percentile, sell_volume, sell_avg, sell_max,
                        sell_min, sell_stddev, sell_median, sell_percentile)
                    SELECT %(typeid)s, %(locationid)s, current_timestamp,
                    %(buy_volume)s, %(buy_avg)s, %(buy_max)s, %(buy_min)s,
                    %(buy_stddev)s, %(buy_median)s, %(buy_percentile)s,
                    %(sell_volume)s, %(sell_avg)s, %(sell_max)s, %(sell_min)s,
                    %(sell_stddev)s, %(sell_median)s, %(sell_percentile)s
                    WHERE NOT EXISTS (SELECT * FROM upsert)''', tuple(price_data))
                self.log.debug('Block done, %d items for location %s' % (len(price_data), system[1]))
                self.dqueue.task_done()

        self.pool.putconn(conn)


if __name__ == '__main__':
    ps = PriceSpinner('stationspinner.ini')
    ps.refresh_evecentral_prices()
