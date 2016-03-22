# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0042_auto_20160102_1808'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contact',
            unique_together=set([('owner', 'listType', 'contactID')]),
        ),
    ]
