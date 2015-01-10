# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stationspinner.libs.fields

def merge_mailmessages(apps, schema_editor):
    Old = apps.get_model('character', 'TempMailMessage')
    New = apps.get_model('character', 'MailMessage')
    db_alias = schema_editor.connection.alias

    msg_ids = [m['messageID'] for m in Old.objects.using(db_alias).
        all().distinct('messageID').values('messageID')]

    for msg_id in msg_ids:
        messages = Old.objects.using(db_alias).filter(messageID=msg_id)
        head = messages[0]
        tail = messages[1:]
        new_message = New.objects.using(db_alias).create(messageID=msg_id,
                          title=head.title,
                          senderName=head.senderName,
                          senderID=head.senderID,
                          toCorpOrAllianceID=head.toCorpOrAllianceID,
                          sentDate=head.sentDate,
                          toListID=head.toListID,
                          toCharacterIDs=head.toCharacterIDs,
                          raw_message=head.raw_message,
                          parsed_message=head.parsed_message,
                          broken=head.broken)
        new_message.owners.add(head.owner)
        for dupe in tail:
            new_message.owners.add(dupe.owner)
            dupe.delete()
        new_message.save()


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0016_auto_20150102_0924'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MailMessage',
            new_name='TempMailMessage'
        ),
        migrations.CreateModel(
            name='MailMessage',
            fields=[
                ('messageID', models.BigIntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('senderName', models.CharField(max_length=255, null=True, blank=True)),
                ('senderID', models.IntegerField()),
                ('toCorpOrAllianceID', models.TextField(default=b'', blank=True)),
                ('sentDate', stationspinner.libs.fields.DateTimeField()),
                ('owners', models.ManyToManyField(to='character.CharacterSheet', null=True)),
                ('toListID', models.TextField(default=b'', blank=True)),
                ('toCharacterIDs', models.TextField(default=b'', blank=True)),
                ('raw_message', models.TextField(default=b'', blank=True)),
                ('parsed_message', models.TextField(default=b'', blank=True, null=True)),
                ('broken', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(
            merge_mailmessages,
        ),
        migrations.DeleteModel(
            name='TempMailMessage'
        ),
    ]
