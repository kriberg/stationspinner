# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0029_assets_container_value'),
    ]

    operations = [
        migrations.RunSQL(
            sql = '''
            CREATE OR REPLACE VIEW character_assetsummary AS
              SELECT
                a.owner_id,
                a."locationID",
                sum(item_value)  AS "locationValue",
                sum(item_volume) AS "locationVolume"
              FROM character_asset a
              WHERE (owner_id, "locationID") IN (
                SELECT
                  owner_id,
                  "locationID"
                FROM
                  character_asset
                GROUP BY
                  owner_id,
                  "locationID")
              GROUP BY a.owner_id, a."locationID"
              ORDER BY a.owner_id, a."locationID";
            COMMIT;
            '''
        ),
    ]
