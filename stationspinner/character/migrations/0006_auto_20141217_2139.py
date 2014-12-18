# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0005_auto_20141217_2137'),
    ]

    operations = [
        migrations.RenameField(
            model_name='characterimplant',
            old_name='character',
            new_name='owner',
        ),
        migrations.RenameField(
            model_name='jumpclone',
            old_name='character',
            new_name='owner',
        ),
        migrations.AlterUniqueTogether(
            name='jumpclone',
            unique_together=set([('owner', 'jumpCloneID')]),
        ),
    ]
