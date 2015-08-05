from abc import ABCMeta
from django.db import connections
from redis import Redis
from stationspinner.libs.pragma import *
import json

REDIS_ASSET_CACHE = 2


class BaseAssetHandler():
    __metaclass__ = ABCMeta
    redis = Redis(db=REDIS_ASSET_CACHE)

    def _merge_query(self):
        return '''
        SELECT
            ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(locations)))
        FROM
            (SELECT
                "locationID",
                SUM("locationValue") as "locationValue",
                SUM("locationVolume") as "locationVolume"
            FROM
                {0}
            WHERE
                owner_id IN %s
            GROUP BY "locationID"
            ORDER BY "locationID") locations
        '''.format(self.ASSETSUMMARY_VIEW)

    def _cache_data(self, key, data):
        self.redis.set(key, json.dumps(data))

    def _cache_get(self, key):
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        else:
            return None

    def _entity_key(self, entities):
        return 'entities:{0}'.format(','.join(map(str, entities)))

    def _location_key(self, locationID):
        return 'location:{0}'.format(locationID)


    def get_merged_asset_locations(self, entities):
        keyset = self._entity_key(entities)
        asset_locations = self._cache_get(keyset)

        if not asset_locations:
            with connections['default'].cursor() as cursor:
                cursor.execute(self._merge_query(), (entities,))
                asset_locations = cursor.fetchone()[0]
                self.annotate_locations(asset_locations)
                self._cache_data(keyset, asset_locations)
        else:
            print keyset, 'assets cached'

        return asset_locations

    def annotate_locations(self, asset_locations):
        for asset_location in asset_locations:
            locationID = asset_location['locationID']
            location_key = self._location_key(locationID)
            location_data = self._cache_get(locationID)
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
        search_key = 'entities:*{0}*'.format(entity)
        result = self.redis.scan(match=search_key)
        while True:
            cursor = result[0]
            keys = result[1]
            if len(keys) > 0:
                self.redis.delete(*keys)
            result = self.redis.scan(match=search_key, cursor=cursor)
            if cursor == 0L:
                break




class CharacterAssetHandler(BaseAssetHandler):
    ASSETSUMMARY_VIEW = 'character_assetsummary'


class CorporationAssetHandler(BaseAssetHandler):
    ASSETSUMMARY_VIEW = 'corporation_assetsummary'
