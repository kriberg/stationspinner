from abc import ABCMeta
from django.db import connections
from redis import Redis
from stationspinner.libs.pragma import *
import json

REDIS_ASSET_CACHE = 2


class BaseAssetHandler():
    __metaclass__ = ABCMeta
    redis = Redis(db=REDIS_ASSET_CACHE)

    def _merge_query(self, locationIDs):
        if len(locationIDs) > 0:
            search_query = ''' AND v."locationID" IN (
                SELECT
                    DISTINCT(a."locationID")
                FROM
                    {0}_asset a
                WHERE
                    a."regionID" IN %(locationIDs)s OR
                    a."solarSystemID" IN %(locationIDs)s OR
                    a."locationID" IN %(locationIDs)s
            )'''.format(self.ASSET_TYPE)
        else:
            search_query = ''

        return '''
        SELECT
            COALESCE(
                ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(locations))),
                '[]'
            )
        FROM
            (SELECT
                v."locationID",
                SUM(v."locationValue") as "value",
                SUM(v."locationVolume") as "volume"
            FROM
                {0} v
            WHERE
                v.owner_id IN %(owner_id)s
                {1}
            GROUP BY v."locationID"
            ORDER BY v."locationID") locations
        '''.format(
            self.ASSETSUMMARY_VIEW,
            search_query
        )

    def _asset_query(self, entities, locationID, parent_id):
        clauses = ['a.owner_id IN %(owner_id)s']
        if parent_id:
            clauses.append('a.parent_id = %(parent_id)s')
        else:
            clauses.append('a.parent_id IS NULL')
        if locationID:
            clauses.append('a."locationID" = %(locationID)s')

        sql =  '''
        SELECT
            COALESCE(
                ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(t))),
                '[]'
            )
        FROM (
            SELECT
                a."itemID",
                a."typeID",
                a."typeName" as name,
                a.quantity,
                a.flag,
                a."groupID",
                a.singleton,
                a."rawQuantity",
                a.item_volume as volume,
                a.item_value as value,
                a.container_value,
                a.container_volume,
                a.owner_id as owner,
                n."itemName"
            FROM
                {0}_asset a
            LEFT OUTER JOIN {0}_itemlocationname n USING ("itemID", owner_id)
            WHERE
                {1}
            ) t
        '''.format(
            self.ASSET_TYPE,
            ' AND \n'.join(clauses)
        )
        return sql


    def _cache_data(self, key, data):
        self.redis.set(key, json.dumps(data))

    def _cache_get(self, key):
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        else:
            return None

    def _entity_key(self, entities, locationIDs):
        return 'entities:{0}:{1}'.format(
            ','.join(map(str, entities)),
            ','.join(map(str, locationIDs))
        )

    def _location_data_key(self, locationID):
        return 'location_data:{0}'.format(locationID)

    def _asset_key(self, entites, locationID, parentID):
        return 'assets:{0}:{1}:{2}'.format(
            ','.join(map(str, entites)),
            locationID,
            parentID
        )

    def get_merged_asset_locations(self, entities, locationIDs=[]):
        keyset = self._entity_key(entities, locationIDs)

        asset_locations = self._cache_get(keyset)

        if not asset_locations:
            with connections['default'].cursor() as cursor:
                cursor.execute(
                    self._merge_query(locationIDs),
                    {
                        'owner_id': tuple(entities),
                        'locationIDs': tuple(locationIDs)
                    }
                )
                asset_locations = cursor.fetchone()[0]
                self.annotate_locations(asset_locations)
                self._cache_data(keyset, asset_locations)

        return asset_locations

    def annotate_locations(self, asset_locations):
        for asset_location in asset_locations:
            locationID = asset_location['locationID']
            location_key = self._location_data_key(locationID)
            location_data = self._cache_get(location_key)
            if not location_data:
                location = get_location(locationID)
                location_data = {
                    'regionName': get_location_regionName(location),
                    'regionID': get_location_regionID(location),
                    'solarSystemName': get_location_solarSystemName(location),
                    'solarSystemID': get_location_solarSystemID(location),
                    'name': get_location_name(locationID)
                }
                self._cache_data(location_key, location_data)
            asset_location.update(location_data)

    def invalidate_entity(self, entity):
        search_keys = ('entities:*{0}*'.format(entity),
                       'assets:*{0}*'.format(entity))
        for search_key in search_keys:
            result = self.redis.scan(match=search_key)
            while True:
                cursor = result[0]
                keys = result[1]
                if len(keys) > 0:
                    self.redis.delete(*keys)
                result = self.redis.scan(match=search_key, cursor=cursor)
                if cursor == 0L:
                    break


    def get_location_assets(self,
                            entities,
                            locationID=None,
                            parent_id=None):
        keyset = self._asset_key(entities, locationID, parent_id)
        assets = self._cache_get(keyset)

        if not assets:
            with connections['default'].cursor() as cursor:
                q = self._asset_query(entities, locationID, parent_id)
                cursor.execute(q, {
                    'owner_id': entities,
                    'locationID': locationID,
                    'parent_id': parent_id
                })
                assets = cursor.fetchone()[0]
                self._cache_data(keyset, assets)
        return assets



class CharacterAssetHandler(BaseAssetHandler):
    ASSETSUMMARY_VIEW = 'character_assetsummary'
    ASSET_TYPE = 'character'


class CorporationAssetHandler(BaseAssetHandler):
    ASSETSUMMARY_VIEW = 'corporation_assetsummary'
    ASSET_TYPE = 'corporation'
