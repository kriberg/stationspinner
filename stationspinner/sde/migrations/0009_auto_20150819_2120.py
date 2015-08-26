# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sde', '0008_auto_20150715_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invgroup',
            name='categoryID',
        ),
        migrations.RemoveField(
            model_name='invtype',
            name='groupID',
        ),
        migrations.RemoveField(
            model_name='invtype',
            name='marketGroupID',
        ),
        migrations.RemoveField(
            model_name='invtype',
            name='raceID',
        ),
        migrations.AddField(
            model_name='invgroup',
            name='category',
            field=models.ForeignKey(db_column='categoryID', to='sde.InvCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invtype',
            name='group',
            field=models.ForeignKey(db_column='groupID', to='sde.InvGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invtype',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invtype',
            name='marketGroup',
            field=models.ForeignKey(db_column='marketGroupID', to='sde.InvMarketGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invtype',
            name='race',
            field=models.ForeignKey(db_column='raceID', to='sde.ChrRace', null=True),
            preserve_default=True,
        ),
    ]
