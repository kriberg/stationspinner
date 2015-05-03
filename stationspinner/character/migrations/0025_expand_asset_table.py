# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0024_auto_20150307_1918'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE character_asset ADD COLUMN item_volume NUMERIC(30,2);
            ALTER TABLE character_asset ADD COLUMN item_value NUMERIC(30,2);
            ALTER TABLE character_asset ADD COLUMN container_volume NUMERIC(30,2);
            COMMIT;
            '''
        ),
    ]
