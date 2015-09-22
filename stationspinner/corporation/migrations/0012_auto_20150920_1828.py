# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0011_auto_20150920_1132'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemLocationName',
            fields=[
                ('itemID', models.BigIntegerField(serialize=False, primary_key=True)),
                ('itemName', models.CharField(max_length=255)),
                ('x', models.BigIntegerField(default=0)),
                ('y', models.BigIntegerField(default=0)),
                ('z', models.BigIntegerField(default=0)),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='itemlocationname',
            unique_together=set([('itemID', 'owner')]),
        ),
    ]
