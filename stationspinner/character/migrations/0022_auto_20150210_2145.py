# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0021_auto_20150202_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransaction',
            name='clientID',
            field=models.BigIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='journalTransactionID',
            field=models.BigIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='transactionID',
            field=models.BigIntegerField(null=True),
            preserve_default=True,
        ),
    ]
