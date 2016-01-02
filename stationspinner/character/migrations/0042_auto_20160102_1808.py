# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0041_auto_20151231_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industryjob',
            name='blueprintLocationID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='industryjob',
            name='completedCharacterID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='industryjob',
            name='facilityID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='industryjob',
            name='installerID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='industryjob',
            name='jobID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='industryjob',
            name='stationID',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='industryjobhistory',
            name='facilityID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='industryjobhistory',
            name='installerID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='industryjobhistory',
            name='jobID',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='industryjobhistory',
            name='stationID',
            field=models.BigIntegerField(null=True),
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
