# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0007_auto_20141217_2251'),
    ]

    operations = [
        migrations.AddField(
            model_name='jumpcloneimplant',
            name='owner',
            field=models.ForeignKey(default=None, to='character.CharacterSheet'),
            preserve_default=False,
        ),
    ]
