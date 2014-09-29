from django.db import models
from django.contrib.auth.models import AbstractUser
#from django_hstore import hstore
#from django.dispatch import receiver


class Capsuler(AbstractUser):
    def __unicode__(self):
        return self.username

    def get_active_keys(self):
        return APIKey.objects.filter(owner=self, expired=False)

#    def get_settings(self):
#        return CapsulerSetting.objects.get(owner=self)
#
#
#class CapsulerSetting(models.Model):
#    settings = hstore.DictionaryField(default={})
#    owner = models.OneToOneField(Capsuler)
#
#    objects = hstore.HStoreManager()
#
#
#@receiver(models.signals.pre_save, sender=Capsuler)
#def add_settings(sender, **kwargs):
#    settings = CapsulerSetting.objects.get_or_create(owner=kwargs['instance'])
#    settings.save()


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

    owner = models.ForeignKey(Capsuler)

    def __unicode__(self):
        return self.name

class APIUpdate(models.Model):
    service = models.CharField(max_length=100)
    last_update = models.DateTimeField(auto_now=True)
    apikey = models.ForeignKey(APIKey)

    class Meta:
        unique_together = ('service', 'apikey')

