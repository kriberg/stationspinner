# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0016_auto_20151126_2130'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='containerlog',
            unique_together=set([('logTime', 'itemID', 'owner')]),
        ),
    ]
