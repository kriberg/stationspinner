# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0018_auto_20150110_1859'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('receiver', models.BigIntegerField()),
                ('type', models.IntegerField(choices=[(0, b'character'), (1, b'corporation_or_alliance'), (2, b'mailing_list')])),
                ('mail', models.ForeignKey(to='character.MailMessage')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mailrecipient',
            unique_together=set([('receiver', 'mail')]),
        ),
        migrations.RemoveField(
            model_name='mailinglist',
            name='id',
        ),
        migrations.AlterField(
            model_name='mailinglist',
            name='listID',
            field=models.BigIntegerField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='mailinglist',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='mailmessage',
            name='toCharacterIDs',
        ),
        migrations.RemoveField(
            model_name='mailmessage',
            name='toCorpOrAllianceID',
        ),
        migrations.RemoveField(
            model_name='mailmessage',
            name='toListID',
        ),
        migrations.AddField(
            model_name='mailinglist',
            name='owners',
            field=models.ManyToManyField(to='character.CharacterSheet'),
            preserve_default=True,
        ),
    ]
