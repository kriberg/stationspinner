from django.db import models
from django.contrib.auth.models import AbstractUser
from django_pgjson.fields import JsonField

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

    owner = models.ForeignKey(Capsuler)

    def __unicode__(self):
        return self.name

class APIUpdate(models.Model):
    service = models.CharField(max_length=100)
    last_update = models.DateTimeField(auto_now=True)
    apikey = models.ForeignKey(APIKey)

    class Meta:
        unique_together = ('service', 'apikey')

