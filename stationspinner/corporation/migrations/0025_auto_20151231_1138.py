# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0024_auto_20151230_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='contactID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='contact',
            name='listType',
            field=models.CharField(max_length=20, choices=[(b'Corporate', b'Corporate'), (b'Alliance', b'Alliance')]),
        ),
        migrations.AlterField(
            model_name='contact',
            name='standing',
            field=models.DecimalField(max_digits=6, decimal_places=3),
        ),
        migrations.AlterUniqueTogether(
            name='contact',
            unique_together=set([('owner', 'contactID', 'listType')]),
        ),
        migrations.RemoveField(
            model_name='contact',
            name='inWatchlist',
        ),
    ]
