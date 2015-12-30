# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0018_auto_20151230_1703'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='industryjob',
            unique_together=set([('facilityID', 'installerID', 'activityID')]),
        ),
        migrations.AlterUniqueTogether(
            name='industryjobhistory',
            unique_together=set([('facilityID', 'installerID', 'activityID')]),
        ),
    ]
