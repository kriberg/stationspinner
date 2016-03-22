# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0044_auto_20160321_2001'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            DELETE FROM character_walletjournal WHERE "refID" IS NULL OR "refTypeID" IS NULL;
            '''
        ),
        migrations.AlterField(
            model_name='walletjournal',
            name='refID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='walletjournal',
            name='refTypeID',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='contactnotification',
            unique_together=set([('owner', 'notificationID')]),
        ),
        migrations.AlterUniqueTogether(
            name='contract',
            unique_together=set([('owner', 'contractID')]),
        ),
        migrations.AlterUniqueTogether(
            name='corporationrole',
            unique_together=set([('owner', 'roleID', 'location')]),
        ),
        migrations.AlterUniqueTogether(
            name='corporationtitle',
            unique_together=set([('owner', 'titleID')]),
        ),
        migrations.AlterUniqueTogether(
            name='medal',
            unique_together=set([('owner', 'medalID')]),
        ),
        migrations.AlterUniqueTogether(
            name='planetarycolony',
            unique_together=set([('owner', 'planetID')]),
        ),
        migrations.AlterUniqueTogether(
            name='research',
            unique_together=set([('owner', 'agentID')]),
        ),
        migrations.AlterUniqueTogether(
            name='skillqueue',
            unique_together=set([('owner', 'typeID', 'level')]),
        ),
        migrations.AlterUniqueTogether(
            name='upcomingcalendarevent',
            unique_together=set([('owner', 'eventID')]),
        ),
        migrations.AlterUniqueTogether(
            name='walletjournal',
            unique_together=set([('refID', 'owner')]),
        ),
    ]
