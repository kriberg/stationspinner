# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0014_auto_20141228_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='broken',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mailmessage',
            name='parsed_message',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mailmessage',
            name='raw_message',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mailmessage',
            name='messageID',
            field=models.BigIntegerField(db_index=True),
            preserve_default=True,
        ),
    ]
