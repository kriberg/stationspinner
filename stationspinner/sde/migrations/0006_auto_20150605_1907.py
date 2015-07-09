# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sde', '0005_auto_20150605_1902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mapdenormalize',
            name='constellationID',
        ),
        migrations.RemoveField(
            model_name='mapdenormalize',
            name='groupID',
        ),
        migrations.RemoveField(
            model_name='mapdenormalize',
            name='orbitID',
        ),
        migrations.RemoveField(
            model_name='mapdenormalize',
            name='regionID',
        ),
        migrations.RemoveField(
            model_name='mapdenormalize',
            name='solarSystemID',
        ),
        migrations.RemoveField(
            model_name='mapdenormalize',
            name='typeID',
        ),
        migrations.AddField(
            model_name='mapdenormalize',
            name='constellation',
            field=models.ForeignKey(related_name='mapdenormalize_constellation', db_column=b'constellationID', to='sde.MapConstellation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mapdenormalize',
            name='group',
            field=models.ForeignKey(related_name='mapdenormalize_group', db_column=b'groupID', to='sde.InvGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mapdenormalize',
            name='orbit',
            field=models.ForeignKey(related_name='mapdenormalize_orbit', db_column=b'orbitID', to='sde.MapDenormalize', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mapdenormalize',
            name='region',
            field=models.ForeignKey(related_name='mapdenormalize_region', db_column=b'regionID', to='sde.MapRegion', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mapdenormalize',
            name='solarSystem',
            field=models.ForeignKey(related_name='mapdenormalize_solarSystem', db_column=b'solarSystemID', to='sde.MapSolarSystem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mapdenormalize',
            name='type',
            field=models.ForeignKey(related_name='mapdenormalize_type', db_column=b'typeID', to='sde.InvType', null=True),
            preserve_default=True,
        ),
    ]
