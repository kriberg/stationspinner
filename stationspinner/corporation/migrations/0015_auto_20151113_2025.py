# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0014_auto_20151023_1602'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE corporation_asset ADD COLUMN "groupID" BIGINT;
            ALTER TABLE corporation_asset DROP COLUMN category;
            COMMIT;
            '''
        ),
    ]
