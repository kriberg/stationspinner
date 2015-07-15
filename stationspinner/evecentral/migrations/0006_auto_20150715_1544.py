# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evecentral', '0005_auto_20141102_2115'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            DELETE FROM evecentral_marketitem;
            '''
        ),
        migrations.AlterUniqueTogether(
            name='marketitem',
            unique_together=set([('typeID', 'locationID')]),
        ),
    ]
