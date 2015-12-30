# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0022_auto_20151230_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industryjob',
            name='completedCharacterID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='industryjobhistory',
            name='completedCharacterID',
            field=models.BigIntegerField(null=True),
        ),
    ]
