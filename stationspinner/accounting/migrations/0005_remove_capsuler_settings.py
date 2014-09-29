# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_auto_20140928_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='capsuler',
            name='settings',
        ),
    ]
