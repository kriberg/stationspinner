# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charactersheet',
            name='owner_key',
            field=models.ForeignKey(to='accounting.APIKey', null=True),
        ),
    ]
