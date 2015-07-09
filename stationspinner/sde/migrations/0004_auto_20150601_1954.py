# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sde', '0003_auto_20150601_1944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mapdenormalize',
            name='constellationID',
            field=models.ForeignKey(related_name='constellation', db_column=b'constellationID', to='sde.MapConstellation', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mapdenormalize',
            name='groupID',
            field=models.ForeignKey(related_name='group', db_column=b'groupID', to='sde.InvGroup', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mapdenormalize',
            name='orbitID',
            field=models.ForeignKey(related_name='orbit', db_column=b'orbitID', to='sde.MapDenormalize', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mapdenormalize',
            name='regionID',
            field=models.ForeignKey(related_name='region', db_column=b'regionID', to='sde.MapRegion', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mapdenormalize',
            name='solarSystemID',
            field=models.ForeignKey(related_name='solarSystem', db_column=b'solarSystemID', to='sde.MapSolarSystem', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mapdenormalize',
            name='typeID',
            field=models.ForeignKey(related_name='type', db_column=b'typeID', to='sde.InvType', null=True),
            preserve_default=True,
        ),
    ]
