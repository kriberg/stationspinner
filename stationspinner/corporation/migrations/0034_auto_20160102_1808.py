# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0033_auto_20160101_2248'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contractitem',
            old_name='rowID',
            new_name='recordID',
        ),
        migrations.AddField(
            model_name='contract',
            name='search_tokens',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='acceptorID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='assigneeID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='endStationID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='issuerCorpID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='contract',
            name='issuerID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='contract',
            name='startStationID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='contractitem',
            name='rawQuantity',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='industryjob',
            name='jobID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='industryjobhistory',
            name='jobID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='contract',
            unique_together=set([('owner', 'contractID')]),
        ),
        migrations.AlterUniqueTogether(
            name='contractitem',
            unique_together=set([('contract', 'owner', 'recordID')]),
        ),
        migrations.AlterUniqueTogether(
            name='industryjob',
            unique_together=set([('owner', 'jobID')]),
        ),
        migrations.AlterUniqueTogether(
            name='industryjobhistory',
            unique_together=set([('owner', 'jobID')]),
        ),
    ]
