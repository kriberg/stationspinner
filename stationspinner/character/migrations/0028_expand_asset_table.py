# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0027_auto_20150518_1938'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE character_asset ADD COLUMN "regionID" BIGINT;
            ALTER TABLE character_asset ADD COLUMN "solarSystemID" BIGINT;
            COMMIT;
            '''
        ),
    ]
