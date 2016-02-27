# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0036_auto_20160209_1931'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            DELETE FROM corporation_walletjournal WHERE "refID" IS NULL OR "accountKey" IS NULL;
            '''
        ),
        migrations.AlterField(
            model_name='walletjournal',
            name='accountKey',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='walletjournal',
            name='refID',
            field=models.BigIntegerField(db_index=True),
        ),
    ]
