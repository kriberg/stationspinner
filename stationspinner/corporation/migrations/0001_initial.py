# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stationspinner.libs.fields
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0001_initial'),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountBalance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accountKey', models.IntegerField()),
                ('balance', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('accountID', models.IntegerField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('asset_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.Asset')),
            ],
            options={
                'abstract': False,
            },
            bases=('character.asset',),
        ),
        migrations.CreateModel(
            name='Blueprint',
            fields=[
                ('blueprint_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.Blueprint')),
            ],
            options={
            },
            bases=('character.blueprint',),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('contact_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.Contact')),
            ],
            options={
            },
            bases=('character.contact',),
        ),
        migrations.CreateModel(
            name='ContainerLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('itemID', models.BigIntegerField()),
                ('typeID', models.IntegerField(null=True)),
                ('itemTypeID', models.IntegerField()),
                ('actorName', models.CharField(max_length=255)),
                ('flag', models.IntegerField()),
                ('locationID', models.IntegerField()),
                ('logTime', stationspinner.libs.fields.DateTimeField()),
                ('passwordType', models.CharField(default=b'', max_length=9, blank=True)),
                ('action', models.CharField(max_length=50)),
                ('actorID', models.IntegerField()),
                ('quantity', models.IntegerField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('contract_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.Contract')),
            ],
            options={
            },
            bases=('character.contract',),
        ),
        migrations.CreateModel(
            name='ContractBid',
            fields=[
                ('contractbid_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.ContractBid')),
            ],
            options={
            },
            bases=('character.contractbid',),
        ),
        migrations.CreateModel(
            name='ContractItem',
            fields=[
                ('contractitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.ContractItem')),
            ],
            options={
            },
            bases=('character.contractitem',),
        ),
        migrations.CreateModel(
            name='CorporationSheet',
            fields=[
                ('enabled', models.BooleanField(default=False)),
                ('corporationID', models.IntegerField(serialize=False, primary_key=True)),
                ('corporationName', models.CharField(max_length=255)),
                ('allianceID', models.IntegerField(null=True)),
                ('allianceName', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(default=b'', blank=True)),
                ('memberLimit', models.IntegerField(null=True)),
                ('taxRate', models.IntegerField()),
                ('factionID', models.IntegerField(default=0, null=True)),
                ('ceoName', models.CharField(max_length=255)),
                ('ceoID', models.IntegerField()),
                ('stationName', models.CharField(max_length=255)),
                ('stationID', models.IntegerField()),
                ('ticker', models.CharField(max_length=10)),
                ('memberCount', models.IntegerField(default=1)),
                ('shares', models.IntegerField(default=1)),
                ('url', models.CharField(default=b'', max_length=255, blank=True)),
                ('owner_key', models.ForeignKey(to='accounting.APIKey')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accountKey', models.IntegerField()),
                ('description', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Facilities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('facilityID', models.BigIntegerField()),
                ('typeID', models.IntegerField()),
                ('typeName', models.CharField(max_length=255)),
                ('solarSystemID', models.IntegerField()),
                ('solarSystemName', models.CharField(max_length=255)),
                ('regionID', models.IntegerField()),
                ('regionName', models.CharField(max_length=255)),
                ('tax', models.IntegerField(default=0)),
                ('starbaseModifier', models.IntegerField(default=0)),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IndustryJob',
            fields=[
                ('industryjob_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.IndustryJob')),
            ],
            options={
            },
            bases=('character.industryjob',),
        ),
        migrations.CreateModel(
            name='IndustryJobHistory',
            fields=[
                ('industryjobhistory_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.IndustryJobHistory')),
            ],
            options={
            },
            bases=('character.industryjobhistory',),
        ),
        migrations.CreateModel(
            name='MarketOrder',
            fields=[
                ('marketorder_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.MarketOrder')),
            ],
            options={
            },
            bases=('character.marketorder',),
        ),
        migrations.CreateModel(
            name='Medal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('medalID', models.BigIntegerField()),
                ('title', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(default=b'', blank=True)),
                ('created', stationspinner.libs.fields.DateTimeField()),
                ('creatorID', models.IntegerField()),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MemberMedal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('medalID', models.BigIntegerField()),
                ('status', models.CharField(max_length=10)),
                ('issued', stationspinner.libs.fields.DateTimeField()),
                ('issuerID', models.IntegerField()),
                ('reason', models.TextField(default=b'', blank=True)),
                ('title', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(default=b'', blank=True)),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MemberSecurity',
            fields=[
                ('corporationrole_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.CorporationRole')),
                ('characterID', models.IntegerField()),
                ('characterName', models.CharField(max_length=255)),
                ('grantable', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=('character.corporationrole',),
        ),
        migrations.CreateModel(
            name='MemberSecurityLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('changeTime', stationspinner.libs.fields.DateTimeField()),
                ('issuerID', models.IntegerField()),
                ('issuerName', models.CharField(max_length=255)),
                ('characterID', models.IntegerField()),
                ('characterName', models.CharField(max_length=255)),
                ('roleLocationType', models.CharField(max_length=255)),
                ('change_type', models.CharField(max_length=3, choices=[(b'New', b'New'), (b'Old', b'Old')])),
                ('roleID', models.BigIntegerField()),
                ('roleName', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MemberTitle',
            fields=[
                ('corporationtitle_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.CorporationTitle')),
                ('characterID', models.IntegerField()),
                ('characterName', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=('character.corporationtitle',),
        ),
        migrations.CreateModel(
            name='MemberTracking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('characterID', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('startDateTime', stationspinner.libs.fields.DateTimeField()),
                ('logonDateTime', stationspinner.libs.fields.DateTimeField(null=True)),
                ('logoffDateTime', stationspinner.libs.fields.DateTimeField()),
                ('locationID', models.IntegerField()),
                ('location', models.CharField(max_length=255)),
                ('shipTypeID', models.IntegerField()),
                ('shipType', models.CharField(default=b'', max_length=255, blank=True)),
                ('roles', models.BigIntegerField(default=0)),
                ('grantableRoles', models.BigIntegerField(default=0)),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NPCStanding',
            fields=[
                ('npcstanding_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.NPCStanding')),
            ],
            options={
            },
            bases=('character.npcstanding',),
        ),
        migrations.CreateModel(
            name='Outpost',
            fields=[
                ('stationID', models.IntegerField(serialize=False, primary_key=True)),
                ('stationName', models.CharField(max_length=255)),
                ('reprocessingEfficiency', models.DecimalField(default=0.0, max_digits=30, decimal_places=10)),
                ('reprocessingStationTake', models.DecimalField(default=0.0, max_digits=30, decimal_places=10)),
                ('officeRentalCost', models.DecimalField(null=True, max_digits=30, decimal_places=2)),
                ('dockingCostPerShipColume', models.DecimalField(default=0.0, max_digits=30, decimal_places=2)),
                ('standingOwnerID', models.IntegerField()),
                ('ownerID', models.IntegerField()),
                ('solarSystemID', models.IntegerField()),
                ('stationTypeID', models.IntegerField()),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OutpostService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serviceName', models.CharField(max_length=255)),
                ('minStanding', models.DecimalField(max_digits=5, decimal_places=2)),
                ('surchargePerBadStanding', models.IntegerField()),
                ('discountPerGoodStanding', models.IntegerField()),
                ('outpost', models.ForeignKey(to='corporation.Outpost')),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Shareholder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('holder_type', models.CharField(max_length=11, choices=[(b'Corporation', b'Corporation'), (b'Character', b'Character')])),
                ('shareholderID', models.IntegerField()),
                ('shareholderName', models.CharField(max_length=255)),
                ('shareholderCorporationID', models.IntegerField(null=True)),
                ('shareholderCorporationName', models.CharField(max_length=255, null=True)),
                ('shares', models.IntegerField(default=1)),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Starbase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('itemID', models.BigIntegerField()),
                ('typeID', models.IntegerField()),
                ('standingOwnerID', models.IntegerField()),
                ('stateTimestamp', stationspinner.libs.fields.DateTimeField()),
                ('state', models.IntegerField()),
                ('onlineTimestamp', stationspinner.libs.fields.DateTimeField()),
                ('locationID', models.IntegerField(null=True)),
                ('moonID', models.IntegerField(null=True)),
                ('general_settings', django_hstore.fields.DictionaryField(default={})),
                ('combat_settings', django_hstore.fields.DictionaryField(default={})),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StarbaseFuel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('typeID', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('owner', models.ForeignKey(to='corporation.CorporationSheet')),
                ('starbase', models.ForeignKey(to='corporation.Starbase')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WalletDivision',
            fields=[
                ('division_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='corporation.Division')),
            ],
            options={
            },
            bases=('corporation.division',),
        ),
        migrations.CreateModel(
            name='WalletJournal',
            fields=[
                ('walletjournal_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.WalletJournal')),
            ],
            options={
            },
            bases=('character.walletjournal',),
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('wallettransaction_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='character.WalletTransaction')),
            ],
            options={
            },
            bases=('character.wallettransaction',),
        ),
        migrations.AlterUniqueTogether(
            name='starbase',
            unique_together=set([('itemID', 'owner')]),
        ),
        migrations.AlterUniqueTogether(
            name='outpostservice',
            unique_together=set([('outpost', 'serviceName', 'owner')]),
        ),
        migrations.AlterUniqueTogether(
            name='outpost',
            unique_together=set([('stationID', 'owner')]),
        ),
        migrations.AlterUniqueTogether(
            name='membermedal',
            unique_together=set([('medalID', 'owner')]),
        ),
        migrations.AlterUniqueTogether(
            name='medal',
            unique_together=set([('medalID', 'owner')]),
        ),
        migrations.AlterUniqueTogether(
            name='facilities',
            unique_together=set([('facilityID', 'owner')]),
        ),
        migrations.AddField(
            model_name='division',
            name='owner',
            field=models.ForeignKey(to='corporation.CorporationSheet'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='division',
            unique_together=set([('accountKey', 'owner')]),
        ),
        migrations.AddField(
            model_name='containerlog',
            name='owner',
            field=models.ForeignKey(to='corporation.CorporationSheet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accountbalance',
            name='owner',
            field=models.ForeignKey(to='corporation.CorporationSheet'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='accountbalance',
            unique_together=set([('accountID', 'owner')]),
        ),
    ]
