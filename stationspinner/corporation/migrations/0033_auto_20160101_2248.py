# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0032_auto_20160101_2227'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('facilityID', models.BigIntegerField()),
                ('typeID', models.IntegerField()),
                ('typeName', models.CharField(max_length=255)),
                ('solarSystemID', models.IntegerField()),
                ('solarSystemName', models.CharField(max_length=255)),
                ('regionID', models.IntegerField()),
                ('regionName', models.CharField(max_length=255)),
                ('tax', models.DecimalField(max_digits=6, decimal_places=3)),
                ('starbaseModifier', models.IntegerField(default=0)),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='facilities',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='facilities',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Facilities',
        ),
        migrations.AlterUniqueTogether(
            name='facility',
            unique_together=set([('facilityID', 'owner')]),
        ),
    ]
