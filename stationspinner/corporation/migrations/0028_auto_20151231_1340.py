# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0027_auto_20151231_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketorder',
            name='typeName',
            field=models.CharField(max_length=255, null=True),
        ),
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
