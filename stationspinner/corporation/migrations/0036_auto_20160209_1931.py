# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0035_auto_20160102_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='containerlog',
            name='actorID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='containerlog',
            name='locationID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='containerlog',
            name='quantity',
            field=models.BigIntegerField(null=True),
        ),
    ]
