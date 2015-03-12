# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0022_auto_20150210_2145'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='wallettransaction',
            unique_together=set([('owner', 'transactionID')]),
        ),
    ]
