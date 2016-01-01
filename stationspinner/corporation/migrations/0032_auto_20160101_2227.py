# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import stationspinner.libs.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0031_auto_20160101_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransaction',
            name='clientID',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='clientName',
            field=models.CharField(default=b'', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='clientTypeID',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='journalTransactionID',
            field=models.BigIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='quantity',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='stationID',
            field=models.BigIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='stationName',
            field=models.CharField(default=b'', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='transactionDateTime',
            field=stationspinner.libs.fields.DateTimeField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='transactionFor',
            field=models.CharField(default=1, max_length=11),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='transactionID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='transactionType',
            field=models.CharField(default=1, max_length=4),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='typeID',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='typeName',
            field=models.CharField(default=b'', max_length=255, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='wallettransaction',
            unique_together=set([('owner', 'transactionID')]),
        ),
    ]
