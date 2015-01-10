# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0017_auto_20150109_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailmessage',
            name='owners',
            field=models.ManyToManyField(to='character.CharacterSheet'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mailmessage',
            name='parsed_message',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mailmessage',
            name='raw_message',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
