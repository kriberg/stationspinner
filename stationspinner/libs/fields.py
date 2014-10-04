from django.db import models
from datetime import datetime
from stationspinner.libs.eveapi import eveapi
import pytz

class DateTimeField(models.DateTimeField):

    def get_prep_value(self, value):
        if type(value) is eveapi.Element:
            try:
                value = value.data
            except AttributeError:
                pass
        if type(value) is unicode:
            if len(value) == 0:
                value = None

        if type(value) is int:
            try:
                value = datetime.fromtimestamp(value, pytz.UTC)
            except:
                pass

        return super(DateTimeField, self).get_prep_value(value)

