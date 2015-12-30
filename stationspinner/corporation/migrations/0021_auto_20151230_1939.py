# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0020_auto_20151230_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industryjob',
            name='facilityID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='industryjob',
            name='installerID',
            field=models.BigIntegerField(),
        ),
    ]
