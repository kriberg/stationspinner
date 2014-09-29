from django.db import models
from datetime import datetime
import pytz

class DateTimeField(models.DateTimeField):
    def get_prep_value(self, value):
        if type(value) is int:
            try:
                value = datetime.fromtimestamp(value, pytz.UTC)
            except:
                pass
        return super(DateTimeField, self).get_prep_value(value)

