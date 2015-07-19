# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sde', '0007_remove_invtype_chanceofduplicating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invcategory',
            name='description',
        ),
        migrations.RemoveField(
            model_name='invgroup',
            name='allowManufacture',
        ),
        migrations.RemoveField(
            model_name='invgroup',
            name='allowRecycler',
        ),
        migrations.RemoveField(
            model_name='invgroup',
            name='description',
        ),
    ]
