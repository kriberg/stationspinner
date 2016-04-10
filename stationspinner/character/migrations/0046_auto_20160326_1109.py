# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0045_auto_20160321_2204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industryjobhistory',
            name='blueprintLocationID',
            field=models.BigIntegerField(null=True),
        ),
    ]
