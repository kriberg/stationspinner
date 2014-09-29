from django.db import models
from datetime import datetime
from stationspinner.libs import fields as custom

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
        self.closed = False
        self.save()
        current_members = []
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
            exmember.endDate = datetime.now()
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
        return self.name

    class Meta:
        unique_together = ('accessMask', 'type')

