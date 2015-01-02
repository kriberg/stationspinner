# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0015_auto_20150101_2241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailmessage',
            name='toCorpOrAllianceID',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]
