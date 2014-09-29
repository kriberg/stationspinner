# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('universe', '0005_alliance_enddate'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='apicall',
            unique_together=set([('accessMask', 'type')]),
        ),
    ]
