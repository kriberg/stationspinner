# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from stationspinner.evemail.models import update_search_index

def populate_evemail_mailstatus(apps, schema_editor):
    MailMessage = apps.get_model('character', 'MailMessage')
    MailStatus = apps.get_model('evemail', 'MailStatus')
    db_alias = schema_editor.connection.alias
    for instance in MailMessage.objects.using(db_alias).all():
        for character in instance.owners.all():
            MailStatus.objects.using(db_alias).get_or_create(message=instance,
                                                       owner=character.owner)
    update_search_index()

class Migration(migrations.Migration):

    dependencies = [
        ('character', '0019_auto_20150114_2158'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MailStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('read', models.BooleanField(default=False)),
                ('message', models.ForeignKey(to='character.MailMessage')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mailstatus',
            unique_together=set([('message', 'owner')]),
        ),
        migrations.RunSQL(
            sql = '''
                CREATE TABLE evemail_searchindex (
                    "messageID" BIGINT NOT NULL,
                    index_language REGCONFIG NOT NULL,
                    document TSVECTOR,
                    PRIMARY KEY ("messageID", index_language),
                    FOREIGN KEY ("messageID") REFERENCES character_mailmessage ("messageID")
                );

                CREATE UNIQUE INDEX evemail_searchindex_messageid_asdf708123kasd_uniq ON evemail_searchindex USING BTREE ("messageID", index_language);
                ''',
            reverse_sql = 'DROP TABLE evemail_searchindex;'
        ),

        migrations.RunPython(
            populate_evemail_mailstatus,
        ),
    ]
