from django.db import models
from django.contrib.auth.models import AbstractUser
from django_pgjson.fields import JsonField
from datetime import datetime
from pytz import UTC
from stationspinner.libs import fields as custom
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver
from stationspinner.universe.models import APICall
from stationspinner.celery import app

class Capsuler(AbstractUser):
    settings = JsonField(blank=True, default={})
    owner_hash = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.username

    def get_active_keys(self):
        return APIKey.objects.filter(owner=self.pk, expired=False)

    def is_owner(self, obj):
        if type(obj.owner) is Capsuler:
            return obj.owner == self
        else:
            return obj.owner.owner == self


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
    brokeness = models.IntegerField(default=0)
    characterID = models.BigIntegerField(null=True, blank=True)
    corporationID = models.BigIntegerField(null=True, blank=True)
    characterIDs = JsonField(null=True, default=[])

    owner = models.ForeignKey(Capsuler)

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.keyID)

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
    cached_until = custom.DateTimeField(null=True)

    def updated(self, api):
        self.last_update = datetime.fromtimestamp(api._meta.currentTime, tz=UTC)
        self.cached_until = datetime.fromtimestamp(api._meta.cachedUntil, tz=UTC)
        self.save()

    def __unicode__(self):
        return u'{0} {1} {2}'.format(self.apicall,
                                     self.apikey,
                                     self.owner)

    class Meta(object):
        unique_together = ('apicall', 'apikey', 'owner')


@receiver(post_save, sender=Capsuler)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=APIKey)
def validate_key(sender, instance=None, created=False, **kwargs):
    if created:
        app.send_task('accounting.validate_key', (instance.pk,))

@receiver(post_save, sender=APIUpdate)
def sheet_listener(sender, instance=None, created=False, **kwargs):
    if created:
        calls = APICall.objects.filter(name__in=('CorporationSheet', 'CharacterSheet'))
        if instance.apicall in calls:
            app.send_task('accounting.update_apikey_sheets', (instance.apikey.pk,))

