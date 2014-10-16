from stationspinner.libs import get_location_name
from stationspinner.libs.eveapi import eveapi
from stationspinner.libs.eveapi_cache import RedisCache
from stationspinner.sde.models import InvType

import logging

log = logging.getLogger(__name__)


eveapi.set_user_agent('stationspinner//vittoros@#eve-dev')

class EveAPIHandler():
    """
    A wrapper for Entity's eveapi library, which takes care of caching and
    autoboxing api data into a django model.
    """
    def get_eveapi(self):
        """
        Creates an api connection with the proper caching.
        :return: eveapi.EVEAPIConnection
        """
        return eveapi.EVEAPIConnection(cacheHandler=RedisCache())

    def get_authed_eveapi(self, apikey):
        api = eveapi.EVEAPIConnection(cacheHandler=RedisCache())
        return api.auth(keyID=apikey.keyID, vCode=apikey.vCode)

    def _create_defaults(self, result, field_names):
        """

        :param result: The data from eveapi
        :param field_names: The data model's fields
        :return: A dict with the values from the api which matches the field names
        """
        defaults = {}
        if type(result) is eveapi.Element:
            attributes = filter(lambda x: not x.startswith('_'), dir(result))
        elif type(result) is eveapi.Row:
            attributes = result._cols
        else:
            attributes = ()

        for attribute in attributes:
            if attribute in field_names:
                defaults[attribute] = getattr(result, attribute)
        return defaults

    def autoparse(self, result, obj, ignore=()):
        """
        Tries to match the field names of the django model with the results
        from the eveapi. If the names match up, set the model values for those
        given matches.
        :param result: The data from eveapi
        :param obj: The target django model
        :return: None
        """
        kwargs = self._create_defaults(result, obj._meta.get_all_field_names())
        for attribute, value in kwargs.items():
            if attribute in ignore:
                continue
            setattr(obj, attribute, value)
        return obj

    def autoparseObj(self,
                     entry,
                     objClass,
                     unique_together=(),
                      extra_selectors={},
                      owner=None,
                      exclude=(),
                      pre_save=False):

        selectors = {}
        for column in unique_together:
            selectors[column] = getattr(entry, column)

        for key, value in extra_selectors.items():
            selectors[key] = value

        defaults = self._create_defaults(entry,
                                        objClass._meta.get_all_field_names())

        for field in exclude:
            if field in defaults:
                defaults.pop(field)

        if len(selectors) > 0:
            obj, created = objClass.objects.update_or_create(defaults=defaults,
                                                             **selectors)
        else:
            obj = objClass(**defaults)

        if owner:
            obj.owner = owner

        if pre_save:
            obj.save()

        if 'update_from_api' in dir(obj):
            obj.update_from_api(entry, self)

        return obj

    def autoparseList(self,
                      result,
                      objClass,
                      unique_together=(),
                      extra_selectors={},
                      owner=None,
                      exclude=(),
                      pre_save=False,
                      pre_delete=False):

        if pre_delete:
            objClass.objects.all().delete()

        obj_list = []
        for entry in result:
            selectors = {}
            for column in unique_together:
                selectors[column] = getattr(entry, column)

            for key, value in extra_selectors.items():
                selectors[key] = value

            defaults = self._create_defaults(entry,
                                            objClass._meta.get_all_field_names())

            for field in exclude:
                if field in defaults:
                    defaults.pop(field)

            if len(selectors) > 0:
                obj, created = objClass.objects.update_or_create(defaults=defaults,
                                                                 **selectors)
            else:
                obj = objClass(**defaults)

            if owner:
                obj.owner = owner

            if pre_save:
                obj.save()

            if 'update_from_api' in dir(obj):
                obj.update_from_api(entry, self)

            obj_list.append(obj.pk)

        return obj_list

    def asset_parser(self, assets, AssetClass, owner):
        location_cache = {}
        type_cache = {}
        def parse_rowset(rowset, locationID=None, parent=None, path=()):
            contents = []
            for row in rowset:
                if hasattr(row, 'locationID'):
                    locationID = row.locationID

                if locationID in location_cache:
                    locationName = location_cache[locationID]
                else:
                    locationName = get_location_name(locationID)
                    location_cache[locationID] = locationName

                if row.typeID in type_cache:
                    typeName = type_cache[row.typeID]
                else:
                    try:
                        item_type = InvType.objects.get(pk=row.typeID)
                        typeName = item_type.typeName
                    except InvType.DoesNotExist:
                        typeName = None

                item = {
                    'itemID': row.itemID,
                    'locationID': locationID,
                    'locationName': locationName,
                    'typeID': row.typeID,
                    'typeName': typeName,
                    'quantity': row.quantity,
                    'flag': row.flag,
                    'singleton': row.singleton,
                    'parent': parent,
                    'path': path
                }

                if hasattr(row, 'rawQuantity'):
                    item['rawQuantity'] = row.rawQuantity

                asset = AssetClass()
                asset.from_item(item)
                asset.owner = owner
                asset.save()

                if hasattr(row, 'contents'):
                    item['contents'] = parse_rowset(row.contents,
                                                    locationID=locationID,
                                                    parent=row.itemID,
                                                    path=path+(row.itemID,))

                contents.append(item)

            return contents

        store = {}
        AssetClass.objects.filter(owner=owner).delete()

        for container in parse_rowset(assets):
            store[container['itemID']] = container

        return store

