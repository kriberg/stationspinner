# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sde', '0004_auto_20150601_1954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chrancestry',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='chrattribute',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='chrbloodline',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='chrfaction',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='chrfaction',
            name='solarSystemID',
        ),
        migrations.RemoveField(
            model_name='chrrace',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='crpnpccorporation',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='crpnpccorporation',
            name='solarSystemID',
        ),
        migrations.RemoveField(
            model_name='dgmattributetype',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='dgmeffect',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='invcategory',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='invgroup',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='invmarketgroup',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='invmarketgroup',
            name='parentGroupID',
        ),
        migrations.RemoveField(
            model_name='invmetagroup',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='mapconstellation',
            name='regionID',
        ),
        migrations.RemoveField(
            model_name='maplandmark',
            name='iconID',
        ),
        migrations.RemoveField(
            model_name='mapsolarsystem',
            name='regionID',
        ),
        migrations.RemoveField(
            model_name='ramassemblylinestation',
            name='regionID',
        ),
        migrations.RemoveField(
            model_name='ramassemblylinestation',
            name='solarSystemID',
        ),
        migrations.RemoveField(
            model_name='stastation',
            name='constellationID',
        ),
        migrations.RemoveField(
            model_name='stastation',
            name='regionID',
        ),
        migrations.RemoveField(
            model_name='stastation',
            name='solarSystemID',
        ),
        migrations.RemoveField(
            model_name='stastation',
            name='stationTypeID',
        ),
        migrations.AddField(
            model_name='chrancestry',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chrattribute',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chrbloodline',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chrfaction',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chrfaction',
            name='solarSystem',
            field=models.ForeignKey(db_column=b'solarSystemID', to='sde.MapSolarSystem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chrrace',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crpnpccorporation',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='crpnpccorporation',
            name='solarSystem',
            field=models.ForeignKey(db_column=b'solarSystemID', to='sde.MapSolarSystem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dgmattributetype',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dgmeffect',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invcategory',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invgroup',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invmarketgroup',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invmarketgroup',
            name='parentGroup',
            field=models.ForeignKey(db_column=b'parentGroupID', to='sde.InvMarketGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invmetagroup',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mapconstellation',
            name='region',
            field=models.ForeignKey(db_column=b'regionID', to='sde.MapRegion', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='maplandmark',
            name='icon',
            field=models.ForeignKey(db_column=b'iconID', to='sde.EveIcon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mapsolarsystem',
            name='region',
            field=models.ForeignKey(db_column=b'regionID', to='sde.MapRegion', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ramassemblylinestation',
            name='region',
            field=models.ForeignKey(db_column=b'regionID', to='sde.MapRegion', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ramassemblylinestation',
            name='solarSystem',
            field=models.ForeignKey(db_column=b'solarSystemID', to='sde.MapSolarSystem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stastation',
            name='constellation',
            field=models.ForeignKey(db_column=b'constellationID', to='sde.MapConstellation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stastation',
            name='region',
            field=models.ForeignKey(db_column=b'regionID', to='sde.MapRegion', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stastation',
            name='solarSystem',
            field=models.ForeignKey(db_column=b'solarSystemID', to='sde.MapSolarSystem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='stastation',
            name='stationType',
            field=models.ForeignKey(db_column=b'stationTypeID', to='sde.StaStationType', null=True),
            preserve_default=True,
        ),
    ]
