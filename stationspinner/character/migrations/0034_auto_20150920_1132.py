# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0033_auto_20150919_2209'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE character_asset DROP COLUMN search_tokens;
            ALTER TABLE character_asset ADD COLUMN search_tokens TSVECTOR;
            CREATE INDEX character_asset_search_tokens_xa2347xcxoijd ON character_asset USING gin(search_tokens);
            COMMIT;
            '''
        ),
    ]
