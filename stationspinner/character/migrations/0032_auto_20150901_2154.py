# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0031_assets_category'),
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
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='itemlocationname',
            unique_together=set([('itemID', 'owner')]),
        ),
    ]
