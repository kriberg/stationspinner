# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stationspinner.libs.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alliance',
            fields=[
                ('closed', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('shortName', models.CharField(max_length=10)),
                ('allianceID', models.IntegerField(serialize=False, primary_key=True)),
                ('executorCorpID', models.IntegerField(null=True)),
                ('memberCount', models.IntegerField(null=True)),
                ('startDate', stationspinner.libs.fields.DateTimeField(null=True)),
                ('endDate', models.DateField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AllianceMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('corporationID', models.IntegerField()),
                ('startDate', stationspinner.libs.fields.DateTimeField()),
                ('endDate', models.DateField(null=True)),
                ('alliance', models.ForeignKey(to='universe.Alliance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='APICall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accessMask', models.IntegerField()),
                ('type', models.CharField(max_length=11, choices=[(b'Character', b'Character'), (b'Corporation', b'Corporation')])),
                ('name', models.CharField(max_length=50)),
                ('groupID', models.IntegerField()),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='APICallGroup',
            fields=[
                ('groupID', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConquerableStation',
            fields=[
                ('stationID', models.IntegerField(serialize=False, primary_key=True)),
                ('stationName', models.CharField(max_length=255)),
                ('stationTypeID', models.IntegerField()),
                ('solarSystemID', models.IntegerField()),
                ('corporationID', models.IntegerField()),
                ('corporationName', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RefType',
            fields=[
                ('refTypeID', models.IntegerField(serialize=False, primary_key=True)),
                ('refTypeName', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sovereignty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('solarSystemID', models.IntegerField()),
                ('solarSystemName', models.CharField(max_length=255)),
                ('allianceID', models.IntegerField(default=0)),
                ('factionID', models.IntegerField(default=0)),
                ('corporationID', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UniverseUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('apicall', models.CharField(max_length=50)),
                ('last_update', models.DateTimeField(null=True)),
                ('cached_until', stationspinner.libs.fields.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='apicall',
            unique_together=set([('accessMask', 'type')]),
        ),
    ]
