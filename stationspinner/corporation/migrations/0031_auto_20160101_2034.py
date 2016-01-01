# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0030_auto_20160101_1920'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='starbasefuel',
            unique_together=set([('owner', 'starbase', 'typeID')]),
        ),
    ]
