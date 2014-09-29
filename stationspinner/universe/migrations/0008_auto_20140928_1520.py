# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('universe', '0007_auto_20140928_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apicall',
            name='group',
        ),
        migrations.AddField(
            model_name='apicall',
            name='groupID',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
