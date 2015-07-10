# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sde', '0006_auto_20150605_1907'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invtype',
            name='chanceOfDuplicating',
        ),
    ]
