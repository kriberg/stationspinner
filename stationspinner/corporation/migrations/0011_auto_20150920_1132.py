# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0010_auto_20150920_1113'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            ALTER TABLE corporation_asset DROP COLUMN search_tokens;
            ALTER TABLE corporation_asset ADD COLUMN search_tokens TSVECTOR;
            CREATE INDEX corporation_asset_search_tokens_xczvn43562asd ON corporation_asset USING gin(search_tokens);
            COMMIT;
            '''
        ),
    ]
