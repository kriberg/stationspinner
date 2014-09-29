# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('universe', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alliance',
            name='executorCorpID',
            field=models.IntegerField(null=True),
        ),
    ]
