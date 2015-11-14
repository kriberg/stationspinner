# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0013_walletjournal_accountkey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='walletjournal',
            name='refID',
            field=models.BigIntegerField(null=True, db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='walletjournal',
            unique_together=set([('owner', 'refID', 'accountKey')]),
        ),
    ]
