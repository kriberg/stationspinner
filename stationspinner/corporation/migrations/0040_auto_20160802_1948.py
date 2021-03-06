# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-02 19:48
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0039_auto_20160321_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetlist',
            name='items',
            field=django.contrib.postgres.fields.jsonb.JSONField(),
        ),
        migrations.AlterField(
            model_name='membersecuritylog',
            name='newRoles',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[]),
        ),
        migrations.AlterField(
            model_name='membersecuritylog',
            name='oldRoles',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[]),
        ),
        migrations.AlterField(
            model_name='starbase',
            name='combat_settings',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}),
        ),
        migrations.AlterField(
            model_name='starbase',
            name='general_settings',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}),
        ),
    ]
