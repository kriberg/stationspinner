# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stationspinner.libs.fields


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0002_auto_20141209_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='CharacterImplant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('typeID', models.IntegerField()),
                ('typeName', models.CharField(max_length=255)),
                ('character', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JumpClone',
            fields=[
                ('jumpCloneID', models.IntegerField(serialize=False, primary_key=True)),
                ('typeID', models.IntegerField()),
                ('locationID', models.IntegerField()),
                ('cloneName', models.CharField(default=b'', max_length=255, blank=True)),
                ('character', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JumpCloneImplant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('typeID', models.IntegerField()),
                ('typeName', models.CharField(max_length=255)),
                ('jumpCloneID', models.ForeignKey(to='character.JumpClone')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='jumpclone',
            unique_together=set([('character', 'jumpCloneID')]),
        ),
        migrations.RemoveField(
            model_name='charactersheet',
            name='charismaAugmentatorName',
        ),
        migrations.RemoveField(
            model_name='charactersheet',
            name='charismaAugmentatorValue',
        ),
        migrations.RemoveField(
            model_name='charactersheet',
            name='intelligenceAugmentatorName',
        ),
        migrations.RemoveField(
            model_name='charactersheet',
            name='intelligenceAugmentatorValue',
        ),
        migrations.RemoveField(
            model_name='charactersheet',
            name='memoryAugmentatorName',
        ),
        migrations.RemoveField(
            model_name='charactersheet',
            name='memoryAugmentatorValue',
        ),
        migrations.RemoveField(
            model_name='charactersheet',
            name='perceptionAugmentatorName',
        ),
        migrations.RemoveField(
            model_name='charactersheet',
            name='perceptionAugmentatorValue',
        ),
        migrations.RemoveField(
            model_name='charactersheet',
            name='willpowerAugmentatorName',
        ),
        migrations.RemoveField(
            model_name='charactersheet',
            name='willpowerAugmentatorValue',
        ),
        migrations.AddField(
            model_name='charactersheet',
            name='cloneJumpDate',
            field=stationspinner.libs.fields.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charactersheet',
            name='freeRespecs',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charactersheet',
            name='freeSkillPoints',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charactersheet',
            name='homeStationID',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charactersheet',
            name='jumpActivation',
            field=stationspinner.libs.fields.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charactersheet',
            name='jumpFatigue',
            field=stationspinner.libs.fields.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charactersheet',
            name='jumpLastUpdate',
            field=stationspinner.libs.fields.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charactersheet',
            name='lastRespecDate',
            field=stationspinner.libs.fields.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charactersheet',
            name='lastTimedRespec',
            field=stationspinner.libs.fields.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charactersheet',
            name='remoteStationDate',
            field=stationspinner.libs.fields.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
