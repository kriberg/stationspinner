# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0032_auto_20150901_2154'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE character_asset ADD COLUMN search_tokens TEXT;
            COMMIT;
            '''
        ),
    ]
