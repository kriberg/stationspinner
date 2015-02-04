# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields

def populate_mailmessage_receivers(apps, schema_editor):
    MailMessage = apps.get_model('character', 'MailMessage')
    MailRecipient = apps.get_model('character', 'MailRecipient')
    MailingList = apps.get_model('character', 'MailingList')
    EveName = apps.get_model('universe', 'EveName')
    db_alias = schema_editor.connection.alias
    for instance in MailMessage.objects.using(db_alias).all():
        recipients = []
        for recp in MailRecipient.objects.using(db_alias).filter(mail=instance):
            if not recp.type == 2:
                try:
                    name = EveName.objects.using(db_alias).get_name(recp.receiver)
                except:
                    name = recp.receiver
            else:
                try:
                    mailing_list = MailingList.objects.get(pk=recp.receiver)
                    name = mailing_list.displayName
                except:
                    name = 'Mailing list {0}'.format(recp.receiver)
            recipients.append({'name': name,
                               'id': recp.receiver,
                               'type': recp.type})
        instance.receivers = recipients
        instance.save()

class Migration(migrations.Migration):

    dependencies = [
        ('character', '0019_auto_20150114_2158'),
        ('universe', '0003_auto_20150119_1853')
    ]

    operations = [
        migrations.AddField(
            model_name='mailmessage',
            name='receivers',
            field=django_pgjson.fields.JsonBField(default=[], null=True),
            preserve_default=True,
        ),
        migrations.RunPython(
            populate_mailmessage_receivers,
        ),
    ]
