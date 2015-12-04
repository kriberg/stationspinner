# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0015_auto_20151113_2025'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE corporation_asset ADD COLUMN "categoryID" BIGINT;
            COMMIT;
            '''
        ),
    ]
