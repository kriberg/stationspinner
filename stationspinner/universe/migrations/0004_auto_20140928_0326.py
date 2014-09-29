# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('universe', '0003_auto_20140927_1718'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alliance',
            old_name='dissolved',
            new_name='closed',
        ),
        migrations.AddField(
            model_name='alliancemember',
            name='endDate',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
    ]
