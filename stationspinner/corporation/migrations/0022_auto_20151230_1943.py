# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0021_auto_20151230_1939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industryjob',
            name='blueprintLocationID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='industryjobhistory',
            name='blueprintLocationID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='industryjobhistory',
            name='blueprintTypeID',
            field=models.BigIntegerField(null=True),
        ),
    ]
