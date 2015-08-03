# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0006_expand_asset_table'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE corporation_asset ADD COLUMN container_value NUMERIC(30,2);
            COMMIT;
            '''
        ),
    ]
