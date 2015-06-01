from django.db import models
from stationspinner.libs.pragma import get_location_name
from datetime import datetime, timedelta
from pytz import UTC

class Market(models.Model):
    locationID = models.IntegerField()
    cached_until = models.DateTimeField(null=True)

    def updated(self):
        self.cached_until = datetime.now(tz=UTC) + timedelta(hours=6)
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
                self.typeName,
                get_location_name(self.locationID))
        except:
            return u'{0} @ {1}'.format(self.typeName, self.locationID)