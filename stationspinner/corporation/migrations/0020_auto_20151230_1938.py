# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0019_auto_20151230_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industryjobhistory',
            name='facilityID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='industryjobhistory',
            name='installerID',
            field=models.BigIntegerField(),
        ),
    ]
