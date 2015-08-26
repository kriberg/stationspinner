# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0008_assetsummary_init'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE corporation_asset ADD COLUMN category BIGINT;
            COMMIT;
            '''
        ),
    ]
