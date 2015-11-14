# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0038_auto_20151012_1811'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE character_asset ADD COLUMN "groupID" BIGINT;
            ALTER TABLE character_asset DROP COLUMN category;
            COMMIT;
            '''
        ),
    ]
