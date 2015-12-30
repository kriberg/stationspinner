# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0017_auto_20151230_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomsOffice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('itemID', models.BigIntegerField()),
                ('solarSystemID', models.IntegerField()),
                ('solarSystemName', models.CharField(max_length=255)),
                ('reinforceHour', models.IntegerField()),
                ('allowAlliance', models.BooleanField()),
                ('allowStandings', models.BooleanField()),
                ('standingLevel', models.IntegerField()),
                ('taxRateAlliance', models.DecimalField(max_digits=6, decimal_places=3)),
                ('taxRateCorporation', models.DecimalField(max_digits=6, decimal_places=3)),
                ('taxRateStandingHigh', models.DecimalField(max_digits=6, decimal_places=3)),
                ('taxRateStandingGood', models.DecimalField(max_digits=6, decimal_places=3)),
                ('taxRateStandingNeutral', models.DecimalField(max_digits=6, decimal_places=3)),
                ('taxRateStandingBad', models.DecimalField(max_digits=6, decimal_places=3)),
                ('taxRateStandingHorrible', models.DecimalField(max_digits=6, decimal_places=3)),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='customsoffice',
            unique_together=set([('itemID', 'solarSystemID')]),
        ),
    ]
