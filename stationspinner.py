from flask import Flask, Response, abort, make_response, request
from werkzeug.contrib.cache import MemcachedCache
import psycopg2
import ConfigParser

app = Flask(__name__)
cache = MemcachedCache(['127.0.0.1:11211'])

config = ConfigParser.SafeConfigParser()
config.readfp(open('stationspinner.ini'))
db_params = config.items('database')
conn_string = ' '.join(map(lambda a: '%s=%s' % (a[0], a[1]), db_params))
conn = psycopg2.connect(conn_string)

@app.route('/stationspinner/types/')
def invtypes():
    rv = cache.get('types')
    if rv is None:
        with conn.cursor() as cur:
            cur.execute('SELECT array_to_json(array_agg(row_to_json(t))) FROM \
                    (SELECT typeid, typename, marketgroupid FROM \
                    public.invtypes WHERE published=1 AND \
                    volume > 0.0 limit 10) t')
            rv = cur.fetchone()[0]
            cache.set('types', rv)
    return '%s' % rv

@app.route('/stationspinner/marketitems/')
def marketitems():
    rv = cache.get('marketitems')
    if rv is None:
        with conn.cursor() as cur:
            cur.execute('''SELECT array_to_json(array_agg(row_to_json(t))) FROM
                    (SELECT invtypes.typename,
                      mapdenormalize.itemname,
                      (sell_min-buy_max) AS "Profit",
                      CASE WHEN sell_min <> 0 THEN ROUND(100-(buy_max/sell_min*100), 2) ELSE 0 END AS "Profit margin",
                      marketdata."timestamp",
                      marketdata.sell_percentile,
                      marketdata.sell_min,
                      marketdata.buy_percentile,
                      marketdata.buy_max,
                      invmarketgroups.marketgroupname,
                      invcategories.categoryname
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
                      invtypes.typename ASC,
                      mapdenormalize.itemname ASC,
                      invmarketgroups.marketgroupname ASC,
                      invcategories.categoryname ASC,
                      marketdata.buy_volume ASC,
                      marketdata.buy_avg ASC,
                      marketdata.buy_max ASC,
                      marketdata.buy_min ASC,
                      marketdata.buy_stddev ASC,
                      marketdata.buy_median ASC,
                      marketdata.buy_percentile ASC,
                      marketdata.sell_volume ASC,
                      marketdata.sell_avg ASC,
                      marketdata.sell_max ASC,
                      marketdata.sell_min ASC,
                      marketdata.sell_stddev ASC,
                      marketdata.sell_median ASC,
                      marketdata.sell_percentile ASC,
                      marketdata."timestamp" ASC) t''')
            rv = cur.fetchone()[0]
            cache.set('marketitems', rv, timeout=15*60)
    return '%s' % rv

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(config.get('stationspinner', 'log'))
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.debug = True
    app.run()
