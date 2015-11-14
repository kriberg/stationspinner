# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssetWorthEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('registered', models.DateTimeField(auto_now_add=True)),
                ('value', models.DecimalField(max_digits=30, decimal_places=2)),
                ('owner', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='WalletBalanceEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('registered', models.DateTimeField(auto_now_add=True)),
                ('value', models.DecimalField(max_digits=30, decimal_places=2)),
                ('owner', models.IntegerField()),
            ],
        ),
    ]
