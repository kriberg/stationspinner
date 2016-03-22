# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0038_auto_20160321_2002'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='membertracking',
            unique_together=set([('owner', 'characterID')]),
        ),
    ]
