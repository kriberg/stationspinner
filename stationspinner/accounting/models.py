from django.db import models
from django.contrib.auth.models import AbstractUser
from django_pgjson.fields import JsonField
from datetime import datetime
from pytz import UTC

from stationspinner.universe.models import APICall

class Capsuler(AbstractUser):
    settings = JsonField(blank=True, default={})

    def __unicode__(self):
        return self.username

    def get_active_keys(self):
        return APIKey.objects.filter(owner=self, expired=False)


class APIKey(models.Model):
    KEY_TYPES = (
        ('Account', 'Account'),
        ('Character', 'Character'),
        ('Corporation', 'Corporation')
    )

    name = models.CharField(max_length=100)
    keyID = models.CharField(max_length=20)
    vCode = models.CharField(max_length=128)
    accessMask = models.IntegerField(null=True, editable=False)
    type = models.CharField(max_length=11, choices=KEY_TYPES, editable=False, null=True)
    expired = models.BooleanField(default=False, editable=False)
    expires = models.DateTimeField(editable=False, null=True)
    characterID = models.IntegerField(null=True)
    corporationID = models.IntegerField(null=True)

    owner = models.ForeignKey(Capsuler)

    def __unicode__(self):
        return self.name

    def can_call(self, apicall):
        if apicall.accessMask & self.accessMask > 0:
            True
        else:
            False


class APIUpdate(models.Model):
    apicall = models.ForeignKey(APICall)
    apikey = models.ForeignKey(APIKey)
    owner = models.IntegerField()
    last_update = models.DateTimeField(null=True)

    def updated(self):
        self.last_update = datetime.now(tz=UTC)
        self.save()

    def __unicode__(self):
        return u'{0} {1} {2}'.format(self.apicall,
                                     self.apikey,
                                     self.owner)

    class Meta:
        unique_together = ('apicall', 'apikey', 'owner')


