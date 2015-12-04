# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0039_auto_20151113_2021'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE character_asset ADD COLUMN "categoryID" BIGINT;
            COMMIT;
            '''
        ),
    ]
