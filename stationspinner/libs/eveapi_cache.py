from django.core.cache import cache
import logging

log = logging.getLogger(__file__)


class RedisCache(object):
    def retrieve(self, host, path, params):
        key = hash((host, path, frozenset(params.items())))

        cached_data = cache.get(key, None)

    def store(self, host, path, params, doc, obj):
        key = hash((host, path, frozenset(params.items())))

        cacheTimeSeconds = obj.cachedUntil - obj.currentTime

        if cacheTimeSeconds and cacheTimeSeconds > 0:
            cache.set(key, doc, timeout=cacheTimeSeconds)