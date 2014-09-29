# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('universe', '0006_auto_20140928_1437'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apicall',
            old_name='groupID',
            new_name='group',
        ),
    ]
