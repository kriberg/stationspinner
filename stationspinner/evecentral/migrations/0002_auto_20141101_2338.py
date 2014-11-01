# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evecentral', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='marketitem',
            old_name='buy_average',
            new_name='buy_avg',
        ),
        migrations.RenameField(
            model_name='marketitem',
            old_name='buy_maximum',
            new_name='buy_max',
        ),
        migrations.RenameField(
            model_name='marketitem',
            old_name='buy_minimum',
            new_name='buy_min',
        ),
        migrations.RenameField(
            model_name='marketitem',
            old_name='sell_average',
            new_name='sell_avg',
        ),
        migrations.RenameField(
            model_name='marketitem',
            old_name='sell_maximum',
            new_name='sell_max',
        ),
        migrations.RenameField(
            model_name='marketitem',
            old_name='sell_minimum',
            new_name='sell_min',
        ),
    ]
