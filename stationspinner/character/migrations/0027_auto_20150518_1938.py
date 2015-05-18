# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0026_skill_skill_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characterimplant',
            name='owner',
            field=models.ForeignKey(related_name='implants', to='character.CharacterSheet'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jumpclone',
            name='owner',
            field=models.ForeignKey(related_name='jumpClones', to='character.CharacterSheet'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jumpcloneimplant',
            name='jumpCloneID',
            field=models.ForeignKey(related_name='jumpCloneImplants', to='character.JumpClone'),
            preserve_default=True,
        ),
    ]
