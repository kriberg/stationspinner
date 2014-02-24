import psycopg2
import logging
import sys
import ConfigParser
import httplib
import json
from evelink.thirdparty.eve_central import EVECentral

class PriceSpinner():
    BLOCK_SIZE = 100
    MARKET_ITEMS = 'SELECT typeid FROM invtypes WHERE published=1 AND marketgroupid is not null'
    def __init__(self, configfile):
        self.config = ConfigParser.SafeConfigParser()
        self.config.readfp(open(configfile))
        self.log = logging.getLogger('pricespinner')
        handler = logging.FileHandler(self.config.get('pricespinner', 'log'))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)

        db_params = self.config.items('database')
        conn_string = ' '.join(map(lambda a: '%s=%s' % (a[0], a[1]), db_params))
        self.conn = psycopg2.connect(conn_string)
        self.conn.autocommit = True
        self.ec = EVECentral()
    def cursor(self):
        return self.conn.cursor()

    def get_system_ids(self):
        system_names = map(lambda a: a.strip(), self.config.get('pricespinner', 'systems').split(','))
        cur = self.cursor()
        cur.execute('SELECT itemid, itemname FROM mapdenormalize WHERE itemname IN %s', (tuple(system_names),))
        res = cur.fetchall()
        return res

    def pull_prices(self):
        with self.cursor() as cur:
            cur.execute(self.MARKET_ITEMS)
            system_ids = self.get_system_ids()

            block = cur.fetchmany(size=self.BLOCK_SIZE)
            while block:
                typeids = map(lambda t: t[0], block)
                for system in system_ids:
                    yield system, self.ec.market_stats(typeids, system=system)
                block = cur.fetchmany(size=self.BLOCK_SIZE)
    def refresh_market_prices(self):
        with self.cursor() as cur:
            cur.execute('SELECT count(*) FROM invtypes WHERE published=1 AND marketgroupid is not null')
            total_items = cur.fetchone()[0]
        processed_items = 0
        self.log.info('Fetching market prices for %s items' % total_items)
        for location, prices in self.pull_prices():
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
            with self.cursor() as cur:
                price_data = []
                for typeid in prices.keys():
                    price = prices[typeid]
                    type_data = {'typeid': typeid, 'locationid': location[0]}
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
                processed_items += cur.rowcount
                self.log.debug('Block done, %d items for system %s' % (len(price_data), location[1]))
        self.log.info('Processed %s items in total' % processed_items)


if __name__ == '__main__':
    ps = PriceSpinner('stationspinner.ini')
    ps.refresh_market_prices()
