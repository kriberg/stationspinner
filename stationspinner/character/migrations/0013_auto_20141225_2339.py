# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0012_auto_20141225_2329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notificationID',
            field=models.IntegerField(db_index=True),
            preserve_default=True,
        ),
    ]
