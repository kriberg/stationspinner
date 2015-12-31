# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0026_auto_20151231_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shareholder',
            name='shareholderCorporationID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='shareholder',
            name='shareholderID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='shareholder',
            unique_together=set([('owner', 'shareholderID', 'holder_type')]),
        ),
    ]
