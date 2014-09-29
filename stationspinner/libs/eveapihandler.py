from stationspinner.libs.eveapi import eveapi
from stationspinner.libs.eveapi_cache import RedisCache

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

    def autoparse(self, result, obj):
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
            setattr(obj, attribute, value)
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
