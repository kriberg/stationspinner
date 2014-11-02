from django.db import models
from stationspinner.libs.pragma import get_location_name
from stationspinner.sde.models import InvType
from datetime import datetime
from pytz import UTC

class Market(models.Model):
    locationID = models.IntegerField()
    last_updated = models.DateTimeField(null=True)

    def updated(self):
        self.last_updated = datetime.now(tz=UTC)
        self.save()

    def __unicode__(self):
        return get_location_name(self.locationID)

class MarketItem(models.Model):
    typeID = models.IntegerField()
    locationID = models.IntegerField()
    typeName = models.CharField(max_length=255)
    buy_volume = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    buy_avg = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    buy_max = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    buy_min = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    buy_stddev = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    buy_median = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    buy_percentile = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    sell_volume = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    sell_avg = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    sell_max = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    sell_min = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    sell_stddev = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    sell_median = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    sell_percentile = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        try:
            return u'{0} @ {1}'.format(
                InvType.objects.get(pk=self.locationID).typeName,
                get_location_name(self.locationID))
        except:
            return u'{0} @ {1}'.format(self.typeID, self.locationID)