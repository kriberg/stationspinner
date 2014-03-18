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
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute('''SELECT array_to_json(array_agg(row_to_json(t)))::text FROM
                    (SELECT
                        i.typeid,
                        i.name,
                        i.marketgroupid,
                        i.category,
                        CASE
                            WHEN a.valuefloat IS NOT NULL
                                THEN a.valuefloat
                            WHEN a.valueint IS NOT NULL
                                THEN a.valueint
                            ELSE
                                0
                        END AS "meta"
                    FROM
                        (SELECT
                            t.typeid,
                            t.typename as "name",
                            t.marketgroupid,
                            c.categoryname as "category"
                        FROM
                            public.invtypes AS t,
                            public.invgroups AS g,
                            public.invcategories AS c
                        WHERE
                            c.categoryid = g.categoryid AND
                            g.groupid = t.groupid AND
                            t.published=1 AND
                            t.marketgroupid IS NOT NULL) i
                    LEFT OUTER JOIN
                        public.dgmtypeattributes AS a ON a.typeid=i.typeid AND a.attributeID=633
                    ) t''')
            rv = cur.fetchone()[0]
            cache.set('types', rv)
        pool.putconn(conn)
    return '%s' % rv

@app.route('/stationspinner/marketgroups/')
def marketgroups():
    groups = cache.get('marketgroups')
    if groups is None:
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute('''
            WITH RECURSIVE nodes_cte(marketgroupid, marketgroupname, parentgroupid, depth, path) AS
                (SELECT m.marketgroupid, m.marketgroupname, m.parentgroupid, 1::INT AS depth, m.marketgroupname::TEXT AS path FROM invmarketgroups AS m
            UNION ALL SELECT c.marketgroupid, c.marketgroupname, c.parentgroupid, p.depth + 1 AS depth, (p.path || '->' || c.marketgroupname::TEXT)
            FROM nodes_cte AS p, invmarketgroups AS c WHERE c.parentgroupid = p.marketgroupid)
            SELECT array_to_json(array_agg(row_to_json(t)))::text FROM (SELECT * FROM nodes_cte) AS t''')
            groups = cur.fetchone()[0]
        pool.putconn(conn)
        cache.set('marketgroups', groups)
    response = make_response(groups)
    response.mimetype = 'application/json'
    return response

@app.route('/stationspinner/marketdata/')
def marketdata():
    items = cache.get('marketdata')
    if items is None:
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute('''SELECT array_to_json(array_agg(row_to_json(t)))::text FROM
                    (SELECT m.typeid,
                      m.locationid,
                      (m.sell_min-m.buy_max) AS "profit",
                      CASE WHEN m.sell_min <> 0 AND m.buy_max <> 0 THEN
                        ROUND((m.sell_min-m.buy_max)/m.buy_max*100, 2)
                      ELSE
                        0.0
                      END AS "margin",
                      m."timestamp",
                      m.sell_percentile,
                      m.sell_min,
                      m.buy_percentile,
                      m.buy_max,
                      m.buy_volume,
                      m.sell_volume
                    FROM
                      public.marketdata m
                    ) t''')
            items = cur.fetchone()[0]
        pool.putconn(conn)
        cache.set('marketdata', items, timeout=15*60)
    response = make_response(items)
    response.mimetype = 'application/json'
    return response

@app.route('/stationspinner/marketdata/<locationid>')
def location_marketdata(locationid):
    items = cache.get('marketdata_%s' % locationid)
    if items is None:
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute('''SELECT array_to_json(array_agg(row_to_json(t)))::text FROM
                    (SELECT m.typeid,
                      m.locationid,
                      (m.sell_min-m.buy_max) AS "profit",
                      CASE WHEN m.sell_min <> 0 AND m.buy_max <> 0 THEN
                        ROUND((m.sell_min-m.buy_max)/m.buy_max*100, 2)
                      ELSE
                        0.0
                      END AS "margin",
                      m."timestamp",
                      m.sell_percentile,
                      m.sell_min,
                      m.buy_percentile,
                      m.buy_max,
                      m.buy_volume,
                      m.sell_volume
                    FROM
                      public.marketdata m
                    WHERE
                      m.locationid=%s
                    ) t''', (locationid,))
            items = cur.fetchone()[0]
        pool.putconn(conn)
        cache.set('marketdata_%s' % locationid, items, timeout=15*60)
    response = make_response(items)
    response.mimetype = 'application/json'
    return response

@app.route('/stationspinner/marketsystems/')
def marketsystems():
    systems = cache.get('marketsystems')
    if systems is None:
        conn = pool.getconn()
        with conn.cursor() as cur:
            system_names = map(lambda a: a.strip(), config.get('pricespinner', 'systems').split(','))
            cur.execute('''SELECT array_to_json(array_agg(row_to_json(t)))::text FROM
                    (SELECT
                        s.solarsystemid, s.solarsystemname, s.regionid, r.regionname
                    FROM
                        mapsolarsystems s, mapregions r
                    WHERE
                        r.regionid=s.regionid AND
                        s.solarsystemname IN %s) t''', (tuple(system_names),))
            systems = cur.fetchone()[0]
            cache.set('marketsystems', systems)
        pool.putconn(conn)
    response = make_response(systems)
    response.mimetype = 'application/json'
    return response

@app.route('/stationspinner/marketregions/')
def marketregions():
    regions = cache.get('marketregions')
    if regions is None:
        conn = pool.getconn()
        with conn.cursor() as cur:
            region_names = map(lambda a: a.strip(), config.get('pricespinner', 'regions').split(','))
            cur.execute('''SELECT array_to_json(array_agg(row_to_json(t)))::text FROM
                    (SELECT itemid, itemname FROM mapdenormalize WHERE itemname IN %s) t''', (tuple(region_names),))
            regions = cur.fetchone()[0]
            cache.set('marketregions', regions)
        pool.putconn(conn)
    response = make_response(regions)
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
