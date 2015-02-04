from django.db import models
from datetime import datetime
from stationspinner.libs import fields as custom
from stationspinner.libs.eveapi_cache import RedisCache
from stationspinner.libs.eveapi import eveapi
from celery.utils.log import get_task_logger
from pytz import UTC
from traceback import format_exc

log = get_task_logger(__name__)


class Alliance(models.Model):
    closed = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    shortName = models.CharField(max_length=10)
    allianceID = models.IntegerField(primary_key=True)
    executorCorpID = models.IntegerField(null=True)
    memberCount = models.IntegerField(null=True)
    startDate = custom.DateTimeField(null=True)
    endDate = models.DateField(null=True)

    def __unicode__(self):
        return self.name

    def update_from_api(self, result, handler):
        EveName.objects.register(result.allianceID, result.name)
        self.closed = False
        self.save()
        current_members = []
        if hasattr(result, 'memberCorporations'):
            for memberData in result.memberCorporations:
                member, created = AllianceMember.objects.get_or_create(alliance=self,
                                                                       corporationID=memberData.corporationID,
                                                                       startDate=memberData.startDate)
                if created:
                    member.save()
                current_members.append(memberData.corporationID)
            previous_members = AllianceMember.objects.filter(alliance=self) \
                .exclude(corporationID__in=current_members)
            for exmember in previous_members:
                exmember.endDate = datetime.now(tz=UTC)
                exmember.save()
        else:
            exmembers = AllianceMember.objects.filter(alliance=self,
                                          endDate=None)
            for exmember in exmembers:
                exmember.endDate = datetime.now(tz=UTC)
                exmember.save()


class AllianceMember(models.Model):
    alliance = models.ForeignKey(Alliance)
    corporationID = models.IntegerField()
    startDate = custom.DateTimeField()
    endDate = models.DateField(null=True)


class ConquerableStation(models.Model):
    stationID = models.IntegerField(primary_key=True)
    stationName = models.CharField(max_length=255)
    stationTypeID = models.IntegerField()
    solarSystemID = models.IntegerField()
    corporationID = models.IntegerField()
    corporationName = models.CharField(max_length=255)

    def __unicode__(self):
        return self.stationName


class RefType(models.Model):
    refTypeID = models.IntegerField(primary_key=True)
    refTypeName = models.CharField(max_length=255)

    def __unicode__(self):
        return self.refTypeName


class Sovereignty(models.Model):
    solarSystemID = models.IntegerField()
    solarSystemName = models.CharField(max_length=255)
    allianceID = models.IntegerField(default=0)
    factionID = models.IntegerField(default=0)
    corporationID = models.IntegerField(default=0)


    def __unicode__(self):
        return "{0} ({1})".format(self.solarSystemName,
                                  max((self.allianceID, self.factionID)))


class APICallGroup(models.Model):
    groupID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __unicode__(self):
        return self.name


class APICall(models.Model):
    CALL_TYPES = (
        ('Character', 'Character'),
        ('Corporation', 'Corporation')
    )
    accessMask = models.IntegerField()
    type = models.CharField(max_length=11, choices=CALL_TYPES)
    name = models.CharField(max_length=50)
    groupID = models.IntegerField()
    description = models.TextField()

    def __unicode__(self):
        return "{0}.{1}".format(self.type, self.name)

    class Meta:
        unique_together = ('accessMask', 'type')

class UniverseUpdate(models.Model):
    apicall = models.CharField(max_length=50)
    last_update = models.DateTimeField(null=True)
    cached_until = custom.DateTimeField(null=True)

    def updated(self, api):
        self.last_update = datetime.fromtimestamp(api._meta.currentTime, tz=UTC)
        self.cached_until = datetime.fromtimestamp(api._meta.cachedUntil, tz=UTC)
        self.save()


class EveNameManager(models.Manager):
    STEPPING = 200

    def register(self, id, name):
        obj, created = self.get_or_create(pk=id,
                                          defaults={"name": name})
        if created:
            obj.save()
        return obj

    def populate(self):
        unfetched = self.filter(name=None)
        api = eveapi.EVEAPIConnection(cacheHandler=RedisCache())

        for index in xrange(0, unfetched.count(), self.STEPPING):
            block = unfetched[index:index+self.STEPPING]
            ids = [n.id for n in block]
            apidata = api.eve.CharacterName(ids=ids)
            new_ids = []
            for entity in apidata.characters:
                EveName.objects.update_or_create(pk=entity.characterID,
                                                 defaults={'name': entity.name})
                new_ids.append(entity.characterID)
            pruned_ids = set(ids) - set(new_ids)
            self.filter(pk__in=pruned_ids).delete()
            log.info('Fetched {0} names and pruned {1} from EveName.'.format(
                len(new_ids),
                len(pruned_ids)
            ))

    def get_name(self, id):
        try:
            return self.get(pk=id).name
        except:
            pass

        api = eveapi.EVEAPIConnection(cacheHandler=RedisCache())

        try:
            apidata = api.eve.CharacterName(ids=id)
            for entity in apidata.characters:
                self.get_or_create(name=entity.name,
                            id=entity.characterID)
            return self.get(pk=id).name
        except Exception, ex:
            log.warning('No name found for {0}, {1}'.format(id,
                                                            format(ex)))
            return id




class EveName(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True, null=True)

    objects = EveNameManager()

    def __unicode__(self):
        return self.name