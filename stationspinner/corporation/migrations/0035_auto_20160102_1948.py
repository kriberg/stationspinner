# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0034_auto_20160102_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='outpostservice',
            name='stationID',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='outpost',
            name='ownerID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='outpost',
            name='standingOwnerID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='outpost',
            name='stationID',
            field=models.BigIntegerField(serialize=False, primary_key=True),
        ),
        migrations.AlterUniqueTogether(
            name='outpostservice',
            unique_together=set([('stationID', 'serviceName', 'owner')]),
        ),
        migrations.RemoveField(
            model_name='outpostservice',
            name='outpost',
        ),
    ]
