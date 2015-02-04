# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stationspinner.libs.fields
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('evemail', '0002_mail'),
        ('character', '0020_mailmessage_receivers')
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            DROP VIEW evemail_mail;
            CREATE VIEW
                evemail_mail
            AS
                SELECT
                  mail.*,
                  status.read,
                  status.owner_id,
                  1.0 AS relevancy

                FROM
                  evemail_mailstatus status,
                  character_mailmessage mail
                WHERE status.message_id = mail."messageID";
            ''',
            reverse_sql='DROP VIEW evemail_mail'
        ),
    ]
