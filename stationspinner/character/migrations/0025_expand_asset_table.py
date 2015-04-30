# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0023_auto_20150210_2148'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            UPDATE character_wallettransaction SET "transactionFor" = 'p' WHERE "transactionFor" = 'personal';
            UPDATE character_wallettransaction SET "transactionFor" = 'c' WHERE "transactionFor" = 'corporation';
            UPDATE character_wallettransaction SET "transactionType" = 'b' WHERE "transactionType" = 'buy';
            UPDATE character_wallettransaction SET "transactionType" = 's' WHERE "transactionType" = 'sell';
            COMMIT;
            '''
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='transactionFor',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'p', b'Personal'), (b'c', b'Corporation')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='transactionType',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'b', b'Buy'), (b's', b'Sell')]),
            preserve_default=True,
        ),
    ]
