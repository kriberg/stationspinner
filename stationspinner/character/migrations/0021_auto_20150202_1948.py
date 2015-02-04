# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0020_mailmessage_receivers'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='mailrecipient',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='mailrecipient',
            name='mail',
        ),
        migrations.DeleteModel(
            name='MailRecipient',
        ),
    ]
