# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0043_auto_20160316_2124'),
    ]

    operations = [
        migrations.RunSQL('''
        DELETE FROM character_asset;
        DROP INDEX character_asset_compound_owner_id_item_id;
        CREATE UNIQUE INDEX character_asset_compound_owner_id_item_id ON character_asset USING BTREE (owner_id, "itemID");
        ''')
    ]
