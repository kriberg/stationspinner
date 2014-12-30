# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0010_charactersheet_skillpoints'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketorder',
            name='typeName',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='skill',
            name='typeName',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='skillintraining',
            name='typeName',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='skillqueue',
            name='typeName',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
    ]
