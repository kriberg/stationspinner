# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields
import stationspinner.libs.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0002_apiupdate_cached_until'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('itemID', models.BigIntegerField()),
                ('quantity', models.BigIntegerField()),
                ('locationID', models.BigIntegerField()),
                ('locationName', models.CharField(default=b'', max_length=255, blank=True)),
                ('typeID', models.IntegerField()),
                ('typeName', models.CharField(max_length=255)),
                ('flag', models.IntegerField()),
                ('singleton', models.BooleanField(default=False)),
                ('rawQuantity', models.IntegerField(default=0)),
                ('path', models.CharField(default=b'', max_length=255)),
                ('parent_id', models.BigIntegerField(null=True)),
            ],
            options={
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AssetList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('items', django_pgjson.fields.JsonBField()),
                ('retrieved', stationspinner.libs.fields.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Blueprint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('itemID', models.BigIntegerField()),
                ('typeID', models.IntegerField()),
                ('runs', models.IntegerField()),
                ('flagID', models.IntegerField()),
                ('timeEfficiency', models.IntegerField()),
                ('materialEfficiency', models.IntegerField()),
                ('typeName', models.CharField(max_length=255)),
                ('locationID', models.BigIntegerField()),
                ('quantity', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('certificateID', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CharacterSheet',
            fields=[
                ('enabled', models.BooleanField(default=False)),
                ('characterID', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('cloneSkillPoints', models.IntegerField()),
                ('corporationID', models.IntegerField()),
                ('corporationName', models.CharField(max_length=255)),
                ('bloodLine', models.CharField(max_length=50)),
                ('factionID', models.IntegerField(default=None, null=True)),
                ('factionName', models.CharField(default=None, max_length=100, null=True)),
                ('allianceName', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('ancestry', models.CharField(max_length=100)),
                ('balance', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('DoB', stationspinner.libs.fields.DateTimeField()),
                ('gender', models.CharField(max_length=6, choices=[(b'Male', b'Male'), (b'Female', b'Female')])),
                ('race', models.CharField(max_length=20)),
                ('allianceID', models.IntegerField(null=True)),
                ('cloneName', models.CharField(max_length=255, null=True, blank=True)),
                ('charisma', models.IntegerField()),
                ('perception', models.IntegerField()),
                ('intelligence', models.IntegerField()),
                ('memory', models.IntegerField()),
                ('willpower', models.IntegerField()),
                ('charismaAugmentatorValue', models.IntegerField(default=0)),
                ('perceptionAugmentatorValue', models.IntegerField(default=0)),
                ('intelligenceAugmentatorValue', models.IntegerField(default=0)),
                ('memoryAugmentatorValue', models.IntegerField(default=0)),
                ('willpowerAugmentatorValue', models.IntegerField(default=0)),
                ('charismaAugmentatorName', models.CharField(default=None, max_length=255, null=True)),
                ('perceptionAugmentatorName', models.CharField(default=None, max_length=255, null=True)),
                ('intelligenceAugmentatorName', models.CharField(default=None, max_length=255, null=True)),
                ('memoryAugmentatorName', models.CharField(default=None, max_length=255, null=True)),
                ('willpowerAugmentatorName', models.CharField(default=None, max_length=255, null=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('owner_key', models.ForeignKey(to='accounting.APIKey', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('standing', models.IntegerField()),
                ('inWatchlist', models.BooleanField(default=False)),
                ('contactID', models.IntegerField()),
                ('contactName', models.CharField(max_length=255)),
                ('contactTypeID', models.IntegerField()),
                ('listType', models.CharField(max_length=20, choices=[(b'Private', b'Private'), (b'Corporate', b'Corporate'), (b'Alliance', b'Alliance')])),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notificationID', models.BigIntegerField()),
                ('senderID', models.IntegerField()),
                ('senderName', models.CharField(max_length=255)),
                ('messageData', models.TextField(default=b'', blank=b'')),
                ('sentDate', stationspinner.libs.fields.DateTimeField()),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=50)),
                ('startStationID', models.IntegerField(null=True)),
                ('dateCompleted', stationspinner.libs.fields.DateTimeField(null=True)),
                ('collateral', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('assigneeID', models.IntegerField(null=True)),
                ('issuerID', models.IntegerField()),
                ('price', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('endStationID', models.IntegerField(null=True)),
                ('buyout', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('dateExpired', stationspinner.libs.fields.DateTimeField()),
                ('availability', models.CharField(max_length=10)),
                ('numDays', models.IntegerField(null=True)),
                ('volume', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('title', models.CharField(max_length=255)),
                ('acceptorID', models.IntegerField(null=True)),
                ('forCorp', models.BooleanField(default=False)),
                ('dateAccepted', stationspinner.libs.fields.DateTimeField(null=True)),
                ('dateIssued', stationspinner.libs.fields.DateTimeField(null=True)),
                ('reward', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('type', models.CharField(max_length=15)),
                ('issuerCorpID', models.IntegerField()),
                ('contractID', models.BigIntegerField()),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContractBid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bidID', models.BigIntegerField()),
                ('contractID', models.BigIntegerField()),
                ('bidderID', models.BigIntegerField()),
                ('dateBid', stationspinner.libs.fields.DateTimeField()),
                ('amount', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContractItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rowID', models.BigIntegerField()),
                ('typeID', models.IntegerField()),
                ('quantity', models.BigIntegerField()),
                ('rawQuantity', models.IntegerField(null=True)),
                ('singleton', models.BooleanField(default=False)),
                ('included', models.BooleanField(default=True)),
                ('contract', models.ForeignKey(to='character.Contract')),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CorporationRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('roleID', models.BigIntegerField()),
                ('roleName', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=10, choices=[(b'Global', b'Global'), (b'Base', b'Base'), (b'Other', b'Other'), (b'HQ', b'HQ')])),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CorporationTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titleID', models.IntegerField()),
                ('titleName', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IndustryJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(null=True)),
                ('startDate', stationspinner.libs.fields.DateTimeField()),
                ('endDate', stationspinner.libs.fields.DateTimeField()),
                ('probability', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('blueprintTypeName', models.CharField(max_length=255, null=True, blank=True)),
                ('runs', models.IntegerField(null=True)),
                ('outputLocationID', models.BigIntegerField()),
                ('activityID', models.IntegerField()),
                ('cost', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('blueprintTypeID', models.IntegerField(null=True)),
                ('timeInSeconds', models.IntegerField()),
                ('productTypeID', models.IntegerField(null=True)),
                ('completedDate', stationspinner.libs.fields.DateTimeField(null=True)),
                ('completedCharacterID', models.IntegerField(null=True)),
                ('installerName', models.CharField(max_length=255)),
                ('installerID', models.IntegerField()),
                ('facilityID', models.IntegerField()),
                ('pauseDate', stationspinner.libs.fields.DateTimeField(null=True)),
                ('solarSystemName', models.CharField(max_length=255)),
                ('stationID', models.IntegerField(null=True)),
                ('jobID', models.BigIntegerField(null=True)),
                ('teamID', models.IntegerField(null=True)),
                ('productTypeName', models.CharField(max_length=255, null=True, blank=True)),
                ('blueprintLocationID', models.IntegerField(null=True)),
                ('blueprintID', models.BigIntegerField(null=True)),
                ('solarSystemID', models.IntegerField()),
                ('licensedRuns', models.IntegerField(null=True)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IndustryJobHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(null=True)),
                ('startDate', stationspinner.libs.fields.DateTimeField()),
                ('endDate', stationspinner.libs.fields.DateTimeField()),
                ('probability', models.DecimalField(null=True, max_digits=4, decimal_places=2)),
                ('blueprintTypeName', models.CharField(max_length=255, null=True, blank=True)),
                ('runs', models.IntegerField(null=True)),
                ('outputLocationID', models.BigIntegerField()),
                ('activityID', models.IntegerField()),
                ('cost', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('blueprintTypeID', models.IntegerField(null=True)),
                ('timeInSeconds', models.IntegerField()),
                ('productTypeID', models.IntegerField(null=True)),
                ('completedDate', stationspinner.libs.fields.DateTimeField(null=True)),
                ('completedCharacterID', models.IntegerField(null=True)),
                ('installerName', models.CharField(max_length=255)),
                ('installerID', models.IntegerField()),
                ('facilityID', models.IntegerField()),
                ('pauseDate', stationspinner.libs.fields.DateTimeField(null=True)),
                ('solarSystemName', models.CharField(max_length=255)),
                ('stationID', models.IntegerField(null=True)),
                ('jobID', models.BigIntegerField(null=True)),
                ('teamID', models.IntegerField(null=True)),
                ('productTypeName', models.CharField(max_length=255, null=True, blank=True)),
                ('blueprintLocationID', models.IntegerField(null=True)),
                ('blueprintID', models.BigIntegerField(null=True)),
                ('solarSystemID', models.IntegerField()),
                ('licensedRuns', models.IntegerField(null=True)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailingList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('listID', models.IntegerField()),
                ('displayName', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('senderName', models.CharField(max_length=255, null=True, blank=True)),
                ('senderID', models.IntegerField()),
                ('toCorpOrAllianceID', models.IntegerField(null=True)),
                ('sentDate', stationspinner.libs.fields.DateTimeField()),
                ('messageID', models.BigIntegerField()),
                ('toListID', models.TextField(default=b'', blank=True)),
                ('toCharacterIDs', models.TextField(default=b'', blank=True)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MarketOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('orderID', models.BigIntegerField()),
                ('typeID', models.IntegerField()),
                ('volEntered', models.BigIntegerField()),
                ('minVolume', models.BigIntegerField()),
                ('charID', models.IntegerField()),
                ('accountKey', models.IntegerField(default=1000)),
                ('issued', stationspinner.libs.fields.DateTimeField()),
                ('bid', models.BooleanField(default=False)),
                ('range', models.IntegerField()),
                ('escrow', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('stationID', models.IntegerField()),
                ('orderState', models.IntegerField()),
                ('volRemaining', models.BigIntegerField()),
                ('duration', models.IntegerField()),
                ('price', models.DecimalField(max_digits=30, decimal_places=2)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Medal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('medalID', models.BigIntegerField()),
                ('status', models.CharField(max_length=10)),
                ('issued', stationspinner.libs.fields.DateTimeField()),
                ('issuerID', models.IntegerField()),
                ('reason', models.TextField(default=b'', blank=True)),
                ('title', models.CharField(max_length=255, null=True)),
                ('corporationID', models.IntegerField(null=True)),
                ('description', models.TextField(default=b'', blank=True)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('typeID', models.IntegerField()),
                ('notificationID', models.IntegerField()),
                ('sentDate', stationspinner.libs.fields.DateTimeField()),
                ('read', models.BooleanField(default=False)),
                ('senderName', models.CharField(max_length=255)),
                ('senderID', models.IntegerField()),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NPCStanding',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=11, choices=[(b'Agent', b'Agent'), (b'Corporation', b'Corporation'), (b'Faction', b'Faction')])),
                ('fromID', models.IntegerField()),
                ('fromName', models.CharField(max_length=255)),
                ('standing', models.DecimalField(max_digits=5, decimal_places=2)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlanetaryColony',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lastUpdate', stationspinner.libs.fields.DateTimeField()),
                ('solarSystemName', models.CharField(max_length=100)),
                ('planetName', models.CharField(max_length=255)),
                ('upgradeLevel', models.IntegerField()),
                ('numberOfPins', models.IntegerField()),
                ('planetID', models.IntegerField()),
                ('ownerName', models.CharField(max_length=255)),
                ('ownerID', models.IntegerField()),
                ('planetRypeID', models.IntegerField()),
                ('solarSystemID', models.IntegerField()),
                ('planetTypeName', models.CharField(max_length=50)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
                'verbose_name_plural': 'PlanetaryColonies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Research',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pointsPerDay', models.DecimalField(max_digits=10, decimal_places=2)),
                ('researchStartDate', stationspinner.libs.fields.DateTimeField()),
                ('skillTypeID', models.IntegerField()),
                ('agentID', models.IntegerField()),
                ('remainderPoints', models.DecimalField(max_digits=20, decimal_places=10)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('skillpoints', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=0)),
                ('typeID', models.IntegerField()),
                ('published', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(related_name='skills', to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SkillInTraining',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trainingStartSP', models.IntegerField(null=True)),
                ('trainingTypeID', models.IntegerField(null=True)),
                ('trainingDestinationSP', models.IntegerField(null=True)),
                ('currentTQTime', stationspinner.libs.fields.DateTimeField(null=True)),
                ('trainingEndTime', stationspinner.libs.fields.DateTimeField(null=True)),
                ('skillInTraining', models.BooleanField(default=True)),
                ('trainingStartTime', stationspinner.libs.fields.DateTimeField(null=True)),
                ('trainingToLevel', models.IntegerField(null=True)),
                ('owner', models.ForeignKey(related_name='skillInTraining', to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SkillQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('typeID', models.IntegerField()),
                ('endTime', stationspinner.libs.fields.DateTimeField(null=True)),
                ('startTime', stationspinner.libs.fields.DateTimeField(null=True)),
                ('level', models.IntegerField()),
                ('queuePosition', models.IntegerField()),
                ('startSP', models.IntegerField()),
                ('endSP', models.IntegerField()),
                ('owner', models.ForeignKey(related_name='skillQueue', to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UpcomingCalendarEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eventID', models.IntegerField()),
                ('eventTitle', models.CharField(max_length=255, null=True, blank=True)),
                ('importance', models.BooleanField(default=False)),
                ('response', models.CharField(max_length=20)),
                ('ownerName', models.CharField(max_length=255, blank=True)),
                ('duration', models.IntegerField()),
                ('ownerID', models.IntegerField()),
                ('eventDate', stationspinner.libs.fields.DateTimeField()),
                ('eventText', models.TextField(default=b'', blank=True)),
                ('ownerTypeID', models.IntegerField()),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WalletJournal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('taxReceiverID', models.CharField(max_length=255, null=True, blank=True)),
                ('argName1', models.CharField(max_length=255, null=True, blank=True)),
                ('reason', models.CharField(max_length=255, null=True, blank=True)),
                ('date', stationspinner.libs.fields.DateTimeField()),
                ('refTypeID', models.IntegerField(null=True)),
                ('refID', models.BigIntegerField(null=True)),
                ('ownerID2', models.IntegerField(null=True)),
                ('taxAmount', models.CharField(max_length=255, null=True, blank=True)),
                ('ownerID1', models.IntegerField(null=True)),
                ('argID1', models.IntegerField(null=True)),
                ('owner1TypeID', models.IntegerField(null=True)),
                ('ownerName2', models.CharField(max_length=255, null=True, blank=True)),
                ('owner2TypeID', models.IntegerField(null=True)),
                ('ownerName1', models.CharField(max_length=255, null=True, blank=True)),
                ('amount', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('balance', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('typeID', models.IntegerField(null=True)),
                ('clientTypeID', models.IntegerField(null=True)),
                ('transactionFor', models.CharField(max_length=255, null=True, blank=True)),
                ('price', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('clientID', models.IntegerField(null=True)),
                ('journalTransactionID', models.IntegerField(null=True)),
                ('typeName', models.CharField(max_length=255, null=True, blank=True)),
                ('stationID', models.IntegerField(null=True)),
                ('stationName', models.CharField(max_length=255, null=True, blank=True)),
                ('transactionID', models.IntegerField(null=True)),
                ('quantity', models.IntegerField(null=True)),
                ('transactionDateTime', stationspinner.libs.fields.DateTimeField(null=True)),
                ('clientName', models.CharField(max_length=255, null=True, blank=True)),
                ('transactionType', models.CharField(max_length=255, null=True, blank=True)),
                ('owner', models.ForeignKey(to='character.CharacterSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='skill',
            unique_together=set([('typeID', 'owner')]),
        ),
        migrations.AlterUniqueTogether(
            name='npcstanding',
            unique_together=set([('fromID', 'owner')]),
        ),
        migrations.AlterUniqueTogether(
            name='mailmessage',
            unique_together=set([('messageID', 'owner')]),
        ),
        migrations.AlterUniqueTogether(
            name='contractitem',
            unique_together=set([('contract', 'owner', 'rowID')]),
        ),
        migrations.AlterUniqueTogether(
            name='contractbid',
            unique_together=set([('bidID', 'contractID', 'owner')]),
        ),
        migrations.AddField(
            model_name='certificate',
            name='owner',
            field=models.ForeignKey(to='character.CharacterSheet'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='certificate',
            unique_together=set([('certificateID', 'owner')]),
        ),
        migrations.AddField(
            model_name='blueprint',
            name='owner',
            field=models.ForeignKey(to='character.CharacterSheet'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='blueprint',
            unique_together=set([('itemID', 'owner')]),
        ),
        migrations.AddField(
            model_name='assetlist',
            name='owner',
            field=models.ForeignKey(to='character.CharacterSheet'),
            preserve_default=True,
        ),
    ]
