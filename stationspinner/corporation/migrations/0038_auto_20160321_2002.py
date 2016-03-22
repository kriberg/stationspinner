# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0037_auto_20160227_2007'),
    ]

    operations = [
        migrations.RunSQL('''
        DELETE FROM corporation_asset;
        DROP INDEX corporation_asset_compound_owner_id_item_id;
        CREATE UNIQUE INDEX corporation_asset_compound_owner_id_item_id ON corporation_asset USING BTREE (owner_id, "itemID");
        ''')
    ]
