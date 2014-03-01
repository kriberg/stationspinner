from flask import Flask, Response, abort, make_response, request
from werkzeug.contrib.cache import MemcachedCache
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
import ConfigParser

app = Flask(__name__)
cache = MemcachedCache(['127.0.0.1:11211'])

config = ConfigParser.SafeConfigParser()
config.readfp(open('stationspinner.ini'))
db_params = config.items('database')
conn_string = ' '.join(map(lambda a: '%s=%s' % (a[0], a[1]), db_params))
pool = ThreadedConnectionPool(5, 20, conn_string)

@app.route('/stationspinner/types/')
def invtypes():
    rv = cache.get('types')
    if rv is None:
        with pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT array_to_json(array_agg(row_to_json(t))) FROM \
                        (SELECT typeid, typename, marketgroupid FROM \
                        public.invtypes WHERE published=1 AND \
                        volume > 0.0) t')
                rv = cur.fetchone()[0]
                cache.set('types', rv)
    return '%s' % rv

@app.route('/stationspinner/marketitems/')
def marketitems():
    items = cache.get('marketitems')
    if items is None:
        with pool.getconn() as conn:
            with conn.cursor() as cur:
                cur.execute('''SELECT array_to_json(array_agg(row_to_json(t)))::text FROM
                        (SELECT invtypes.typename as item,
                          mapdenormalize.itemname AS "location",
                          (sell_min-buy_max) AS "profit",
                          CASE WHEN sell_min <> 0 AND buy_max <> 0 THEN
                            ROUND((sell_min-buy_max)/buy_max*100, 2)
                          ELSE
                            0.0
                          END AS "margin",
                          marketdata."timestamp",
                          marketdata.sell_percentile,
                          marketdata.sell_min,
                          marketdata.buy_percentile,
                          marketdata.buy_max,
                          marketdata.buy_volume,
                          marketdata.sell_volume,
                          invmarketgroups.marketgroupname as group,
                          invcategories.categoryname as category
                        FROM
                          public.invmarketgroups,
                          public.invcategories,
                          public.invtypes,
                          public.marketdata,
                          public.mapdenormalize,
                          public.invgroups
                        WHERE
                          invmarketgroups.marketgroupid = invtypes.marketgroupid AND
                          invcategories.categoryid = invgroups.categoryid AND
                          marketdata.typeid = invtypes.typeid AND
                          mapdenormalize.itemid = marketdata.locationid AND
                          invgroups.groupid = invtypes.groupid
                        ORDER BY
                          "margin" DESC,
                          "profit" DESC,
                          invtypes.typename ASC,
                          "location" ASC) t''')
                items = cur.fetchone()[0]
        cache.set('marketitems', items, timeout=15*60)
    response = make_response(items)
    response.mimetype = 'application/json'
    return response

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(config.get('stationspinner', 'log'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
