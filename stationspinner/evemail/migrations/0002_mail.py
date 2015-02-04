# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stationspinner.libs.fields
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('evemail', '0001_initial'),
        ('character', '0020_mailmessage_receivers'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('messageID', models.BigIntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('senderName', models.CharField(max_length=255, null=True, blank=True)),
                ('senderID', models.IntegerField()),
                ('sentDate', stationspinner.libs.fields.DateTimeField()),
                ('parsed_message', models.TextField(null=True)),
                ('read', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL))
            ],
            options={
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.RunSQL(
            sql='''
            CREATE VIEW
                evemail_mail
            AS
                SELECT
                  mail.*,
                  status.read,
                  status.owner_id

                FROM
                  evemail_mailstatus status,
                  (SELECT
                     msg."messageID",
                     msg.title,
                     msg."senderName",
                     msg."senderID",
                     msg."sentDate",
                     msg.parsed_message,
                     coalesce (string_agg(names.name, ', '))
                   FROM character_mailmessage msg
                   JOIN character_mailrecipient recp ON recp.mail_id = msg."messageID"
                   JOIN universe_evename names ON names.id = recp.receiver
                   --WHERE msg."messageID"=250516321
                   GROUP BY msg."messageID" ORDER BY msg."messageID") AS mail

            WHERE status.message_id = mail."messageID";
            ''',
            reverse_sql='DROP VIEW evemail_mail'
        ),
    ]
