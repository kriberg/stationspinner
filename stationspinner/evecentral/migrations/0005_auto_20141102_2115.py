# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evecentral', '0004_marketitem_typename'),
    ]

    operations = [
        migrations.RenameField(
            model_name='market',
            old_name='last_updated',
            new_name='cached_until',
        ),
    ]
