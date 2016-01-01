# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0028_auto_20151231_1340'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='membersecurity',
            unique_together=set([('owner', 'characterID', 'roleID', 'location')]),
        ),
        migrations.AlterUniqueTogether(
            name='membertitle',
            unique_together=set([('owner', 'characterID', 'titleID')]),
        ),
    ]
