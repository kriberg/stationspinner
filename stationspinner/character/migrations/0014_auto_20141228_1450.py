# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0013_auto_20141225_2339'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together=set([('owner', 'notificationID')]),
        ),
    ]
