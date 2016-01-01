# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0029_auto_20160101_1857'),
    ]

    operations = [
        migrations.AddField(
            model_name='membermedal',
            name='characterID',
            field=models.BigIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='membermedal',
            name='issuerID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='membermedal',
            unique_together=set([('owner', 'medalID', 'characterID')]),
        ),
        migrations.RemoveField(
            model_name='membermedal',
            name='description',
        ),
        migrations.RemoveField(
            model_name='membermedal',
            name='title',
        ),
    ]
