# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('locationID', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MarketItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('typeID', models.IntegerField()),
                ('locationID', models.IntegerField()),
                ('buy_volume', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('buy_average', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('buy_maximum', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('buy_minimum', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('buy_stddev', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('buy_median', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('buy_percentile', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('sell_volume', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('sell_average', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('sell_maximum', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('sell_minimum', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('sell_stddev', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('sell_median', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('sell_percentile', models.DecimalField(null=True, max_digits=20, decimal_places=2)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
