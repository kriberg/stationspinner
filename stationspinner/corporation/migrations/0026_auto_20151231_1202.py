# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0025_auto_20151231_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='membersecuritylog',
            name='newRoles',
            field=django_pgjson.fields.JsonField(default=[]),
        ),
        migrations.AddField(
            model_name='membersecuritylog',
            name='oldRoles',
            field=django_pgjson.fields.JsonField(default=[]),
        ),
        migrations.AlterUniqueTogether(
            name='membersecuritylog',
            unique_together=set([('owner', 'changeTime', 'characterID', 'roleLocationType')]),
        ),
        migrations.RemoveField(
            model_name='membersecuritylog',
            name='change_type',
        ),
        migrations.RemoveField(
            model_name='membersecuritylog',
            name='roleID',
        ),
        migrations.RemoveField(
            model_name='membersecuritylog',
            name='roleName',
        ),
    ]
