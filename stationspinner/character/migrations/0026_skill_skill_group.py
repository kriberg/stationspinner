# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0025_expand_asset_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='skill_group',
            field=models.CharField(max_length=50, null=True),
            preserve_default=True,
        ),
    ]
