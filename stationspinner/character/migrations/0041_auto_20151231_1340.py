# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0040_auto_20151126_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketorder',
            name='charID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='marketorder',
            name='stationID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='marketorder',
            unique_together=set([('owner', 'orderID')]),
        ),
    ]
