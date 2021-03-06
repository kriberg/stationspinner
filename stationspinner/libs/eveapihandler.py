from stationspinner.libs.pragma import get_location_name
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

    def _create_defaults(self, result, field_names, exclude=()):
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
            if attribute in field_names and not attribute in exclude:
                defaults[attribute] = getattr(result, attribute)
        return defaults

    def autoparse(self, result, obj, exclude=()):
        """
        Tries to match the field names of the django model with the results
        from the eveapi. If the names match up, set the model values for those
        given matches.
        :param result: The data from eveapi
        :param obj: The target django model
        :return: None
        """
        kwargs = self._create_defaults(result, obj._meta.get_all_field_names(), exclude)
        for attribute, value in kwargs.items():
            if attribute in exclude:
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
                     pre_save=False,
                     immutable=False,
                     static_defaults={}):
        """

        :param entry:
        :param objClass:
        :param unique_together:
        :param extra_selectors:
        :param owner:
        :param exclude:
        :param pre_save:
        :param immutable:
        :param static_defaults:
        :return:
        """

        selectors = {}
        for column in unique_together:
            if column in static_defaults:
                selectors[column] = static_defaults[column]
            else:
                selectors[column] = getattr(entry, column)

        for key, value in extra_selectors.items():
            selectors[key] = value

        if immutable:
            obj = objClass.objects.filter(**selectors)
            if obj.count() == 1:
                return obj[0]

        defaults = self._create_defaults(entry,
                                         objClass._meta.get_all_field_names(),
                                         exclude)
        for key, value in static_defaults.items():
                defaults[key] = value

        if len(selectors) > 0 and not immutable:
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

        obj.save()

        return obj

    def autoparse_list(self,
                       result,
                       objClass,
                       unique_together=(),
                       extra_selectors={},
                       owner=None,
                       exclude=(),
                       pre_save=False,
                       pre_delete=False,
                       immutable=False,
                       static_defaults={}):
        """
        This will take most rowsets from the eveapi and create or update model objects,
        as long as the model attributes match those of from the api.
        :param result:
        :param objClass:
        :param unique_together:
        :param extra_selectors:
        :param owner:
        :param exclude:
        :param pre_save:
        :param pre_delete:
        :param immutable:
        :param static_defaults:
        :return:
        """

        if pre_delete:
            objClass.objects.all().delete()

        obj_list = []
        overlap_obj = []
        for entry in result:
            selectors = {}
            for column in unique_together:
                if column in static_defaults:
                    selectors[column] = static_defaults[column]
                else:
                    selectors[column] = getattr(entry, column)

            for key, value in extra_selectors.items():
                selectors[key] = value

            if immutable:
                objs = objClass.objects.filter(**selectors)
                if objs.count() > 0:
                    overlap_obj.extend([obj.pk for obj in objs])
                    continue

            defaults = self._create_defaults(entry,
                                             objClass._meta.get_all_field_names(),
                                             exclude)
            for key, value in static_defaults.items():
                defaults[key] = value

            if len(selectors) > 0 and not immutable:
                try:
                    obj, created = objClass.objects.update_or_create(defaults=defaults,
                                                                     **selectors)
                except ValueError, ve:
                    log.error('Could not save {0} with defaults "{1}" and selectors "{2}".'.format(
                            objClass, defaults, selectors))
                    raise ve
                except Exception, ex:
                    log.error('Could not save {0} with defaults "{1}" and selectors "{2}".'.format(
                            objClass, defaults, selectors))
                    raise ex
            else:
                obj = objClass(**defaults)

            if owner:
                obj.owner = owner

            if pre_save:
                obj.save()

            if hasattr(obj, 'update_from_api'):
                obj.update_from_api(entry, self)

            obj.save()

            obj_list.append(obj.pk)

        if immutable:
            return obj_list, overlap_obj

        return obj_list

    def autoparse_shared_list(self,
                              result,
                              objClass,
                              unique_together,
                              owner,
                              extra_selectors={},
                              exclude=(),
                              pre_save=False):
        """
        This works more or less like autoparse_list, but it will handle M2M relationships
        in the database, to avoid storing identical items like eve mails, which can take a
        lot of space. A big difference though, is that this will do nothing except adding
        a new owner, if the object already exists, instead of trying to update it.

        :param result:
        :param objClass:
        :param unique_together:
        :param owner:
        :param extra_selectors:
        :param exclude:
        :param pre_save:
        :return:
        """
        obj_list = []
        for entry in result:
            selectors = {}
            for column in unique_together:
                selectors[column] = getattr(entry, column)

            for key, value in extra_selectors.items():
                selectors[key] = value

            try:
                obj = objClass.objects.get(**selectors)
                # This means the object is already indexed, so let's just add the extra
                # owner
                obj.owners.add(owner)
                if hasattr(obj, 'update_from_api'):
                    obj.update_from_api(entry, self)
                obj.save()
                continue
            except objClass.DoesNotExist:
                pass

            defaults = self._create_defaults(entry,
                                             objClass._meta.get_all_field_names(),
                                             exclude)

            if len(selectors) > 0:
                try:
                    obj, created = objClass.objects.update_or_create(defaults=defaults,
                                                                     **selectors)
                except ValueError, ve:
                    raise ve
            else:
                obj = objClass(**defaults)

            obj.owners.add(owner)

            if pre_save:
                obj.save()

            if hasattr(obj, 'update_from_api'):
                obj.update_from_api(entry, self)

            obj_list.append(obj.pk)

        return obj_list

    def asset_parser(self, assets, AssetClass, owner, api_update):
        location_cache = {}
        type_cache = {}
        group_cache = {}
        category_cache = {}
        itemIDs_to_names = []
        store = {}

        def asset_with_name(asset):
            '''
            Checks if this asset might have given name.
            :param asset:
            :return:
            '''

            # only singletons have names
            if not asset.singleton:
                return False

            # 5:  bookmarks
            # 7:  modules
            # 8:  ammo
            # 9:  blueprints
            # 17: commodities
            # 18: drones
            # 32: subsystems
            if asset.category() in (5, 7, 8, 9, 17, 18, 32):
                return False

            # 25: corpses
            # 27: offices, need to use the corp endpoints for this
            if asset.typeID in (25, 27):
                return False

            return True

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

                group = None
                category = None
                typeName = None

                if row.typeID in type_cache and row.typeID in group_cache and row.typeID in category_cache:
                    typeName = type_cache[row.typeID]
                    group = group_cache[row.typeID]
                    category = category_cache[row.typeID]
                else:
                    try:
                        item_type = InvType.objects.get(pk=row.typeID)
                        typeName = item_type.typeName
                        group = item_type.group.pk
                        category = item_type.group.category.pk
                        type_cache[row.typeID] = typeName
                        group_cache[row.typeID] = group
                        category_cache[row.typeID] = category
                    except:
                        pass

                item = {
                    'locationID': locationID,
                    'locationName': locationName,
                    'typeID': row.typeID,
                    'typeName': typeName,
                    'quantity': row.quantity,
                    'flag': row.flag,
                    'groupID': group,
                    'categoryID': category,
                    'singleton': row.singleton,
                    'parent_id': parent,
                }

                if hasattr(row, 'rawQuantity'):
                    item['rawQuantity'] = row.rawQuantity

                asset, created = AssetClass.objects.update_or_create(owner=owner,
                                                                     itemID=row.itemID,
                                                                     defaults=item)

                if asset_with_name(asset):
                    itemIDs_to_names.append(str(asset.itemID))

                if hasattr(row, 'contents'):
                    item['contents'] = parse_rowset(row.contents,
                                                    locationID=locationID,
                                                    parent=row.itemID,
                                                    path=path + (row.itemID,))

                item["itemID"] = asset.itemID

                asset.update_from_api(item, self)
                asset.compute_container_volume()
                asset.compute_container_value()
                asset.save(update_fields=['regionID',
                                          'solarSystemID',
                                          'item_value',
                                          'item_volume',
                                          'container_volume',
                                          'container_value'])

                contents.append(item)

            return contents

        AssetClass.objects.filter(owner=owner).delete()

        for container in parse_rowset(assets):
            store[container['itemID']] = container

        return store, itemIDs_to_names
