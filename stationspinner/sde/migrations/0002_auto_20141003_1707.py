# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sde', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agtagent',
            options={'verbose_name': 'agtAgents'},
        ),
        migrations.AlterModelOptions(
            name='agtagenttype',
            options={'verbose_name': 'agtAgentTypes'},
        ),
        migrations.AlterModelOptions(
            name='agtresearchagent',
            options={'verbose_name': 'agtResearchAgents'},
        ),
        migrations.AlterModelOptions(
            name='certcert',
            options={'verbose_name': 'certCerts'},
        ),
        migrations.AlterModelOptions(
            name='certmastery',
            options={'verbose_name': 'certMasteries'},
        ),
        migrations.AlterModelOptions(
            name='certskill',
            options={'verbose_name': 'certSkills'},
        ),
        migrations.AlterModelOptions(
            name='chrancestry',
            options={'verbose_name': 'chrAncestries'},
        ),
        migrations.AlterModelOptions(
            name='chrattribute',
            options={'verbose_name': 'chrAttributes'},
        ),
        migrations.AlterModelOptions(
            name='chrbloodline',
            options={'verbose_name': 'chrBloodlines'},
        ),
        migrations.AlterModelOptions(
            name='chrfaction',
            options={'verbose_name': 'chrFactions'},
        ),
        migrations.AlterModelOptions(
            name='chrrace',
            options={'verbose_name': 'chrRaces'},
        ),
        migrations.AlterModelOptions(
            name='crpactivity',
            options={'verbose_name': 'crpActivities'},
        ),
        migrations.AlterModelOptions(
            name='crpnpccorporation',
            options={'verbose_name': 'crpNPCCorporations'},
        ),
        migrations.AlterModelOptions(
            name='crpnpccorporationdivision',
            options={'verbose_name': 'crpNPCCorporationDivisions'},
        ),
        migrations.AlterModelOptions(
            name='crpnpccorporationresearchfield',
            options={'verbose_name': 'crpNPCCorporationResearchFields'},
        ),
        migrations.AlterModelOptions(
            name='crpnpccorporationtrade',
            options={'verbose_name': 'crpNPCCorporationTrades'},
        ),
        migrations.AlterModelOptions(
            name='crpnpcdivision',
            options={'verbose_name': 'crpNPCDivisions'},
        ),
        migrations.AlterModelOptions(
            name='dgmattributecategory',
            options={'verbose_name': 'dgmAttributeCategories'},
        ),
        migrations.AlterModelOptions(
            name='dgmattributetype',
            options={'verbose_name': 'dgmAttributeTypes'},
        ),
        migrations.AlterModelOptions(
            name='dgmeffect',
            options={'verbose_name': 'dgmEffects'},
        ),
        migrations.AlterModelOptions(
            name='dgmtypeattribute',
            options={'verbose_name': 'dgmTypeAttributes'},
        ),
        migrations.AlterModelOptions(
            name='dgmtypeeffect',
            options={'verbose_name': 'dgmTypeEffects'},
        ),
        migrations.AlterModelOptions(
            name='eveicon',
            options={'verbose_name': 'eveIcons'},
        ),
        migrations.AlterModelOptions(
            name='eveunit',
            options={'verbose_name': 'eveUnits'},
        ),
        migrations.AlterModelOptions(
            name='industryactivity',
            options={'verbose_name': 'industryActivity'},
        ),
        migrations.AlterModelOptions(
            name='industryactivitymaterial',
            options={'verbose_name': 'industryActivityMaterials'},
        ),
        migrations.AlterModelOptions(
            name='industryactivityprobability',
            options={'verbose_name': 'industryActivityProbabilities'},
        ),
        migrations.AlterModelOptions(
            name='industryactivityproduct',
            options={'verbose_name': 'industryActivityProducts'},
        ),
        migrations.AlterModelOptions(
            name='industryactivityrace',
            options={'verbose_name': 'industryActivityRaces'},
        ),
        migrations.AlterModelOptions(
            name='industryactivityskill',
            options={'verbose_name': 'industryActivitySkills'},
        ),
        migrations.AlterModelOptions(
            name='industryblueprint',
            options={'verbose_name': 'industryBlueprints'},
        ),
        migrations.AlterModelOptions(
            name='invcategory',
            options={'verbose_name': 'invCategories'},
        ),
        migrations.AlterModelOptions(
            name='invcontrabandtype',
            options={'verbose_name': 'invContrabandTypes'},
        ),
        migrations.AlterModelOptions(
            name='invcontroltowerresource',
            options={'verbose_name': 'invControlTowerResources'},
        ),
        migrations.AlterModelOptions(
            name='invcontroltowerresourcepurpose',
            options={'verbose_name': 'invControlTowerResourcePurposes'},
        ),
        migrations.AlterModelOptions(
            name='invflag',
            options={'verbose_name': 'invFlags'},
        ),
        migrations.AlterModelOptions(
            name='invgroup',
            options={'verbose_name': 'invGroups'},
        ),
        migrations.AlterModelOptions(
            name='invitem',
            options={'verbose_name': 'invItems'},
        ),
        migrations.AlterModelOptions(
            name='invmarketgroup',
            options={'verbose_name': 'invMarketGroups'},
        ),
        migrations.AlterModelOptions(
            name='invmetagroup',
            options={'verbose_name': 'invMetaGroups'},
        ),
        migrations.AlterModelOptions(
            name='invmetatype',
            options={'verbose_name': 'invMetaTypes'},
        ),
        migrations.AlterModelOptions(
            name='invname',
            options={'verbose_name': 'invNames'},
        ),
        migrations.AlterModelOptions(
            name='invposition',
            options={'verbose_name': 'invPositions'},
        ),
        migrations.AlterModelOptions(
            name='invtrait',
            options={'verbose_name': 'invTraits'},
        ),
        migrations.AlterModelOptions(
            name='invtype',
            options={'verbose_name': 'invTypes'},
        ),
        migrations.AlterModelOptions(
            name='invtypematerial',
            options={'verbose_name': 'invTypeMaterials'},
        ),
        migrations.AlterModelOptions(
            name='invtypereaction',
            options={'verbose_name': 'invTypeReactions'},
        ),
        migrations.AlterModelOptions(
            name='invuniquename',
            options={'verbose_name': 'invUniqueNames'},
        ),
        migrations.AlterModelOptions(
            name='mapcelestialstatistic',
            options={'verbose_name': 'mapCelestialStatistics'},
        ),
        migrations.AlterModelOptions(
            name='mapconstellation',
            options={'verbose_name': 'mapConstellations'},
        ),
        migrations.AlterModelOptions(
            name='mapconstellationjump',
            options={'verbose_name': 'mapConstellationJumps'},
        ),
        migrations.AlterModelOptions(
            name='mapdenormalize',
            options={'verbose_name': 'mapDenormalize'},
        ),
        migrations.AlterModelOptions(
            name='mapjump',
            options={'verbose_name': 'mapJumps'},
        ),
        migrations.AlterModelOptions(
            name='maplandmark',
            options={'verbose_name': 'mapLandmarks'},
        ),
        migrations.AlterModelOptions(
            name='maplocationscene',
            options={'verbose_name': 'mapLocationScenes'},
        ),
        migrations.AlterModelOptions(
            name='maplocationwormholeclass',
            options={'verbose_name': 'mapLocationWormholeClasses'},
        ),
        migrations.AlterModelOptions(
            name='mapregion',
            options={'verbose_name': 'mapRegions'},
        ),
        migrations.AlterModelOptions(
            name='mapregionjump',
            options={'verbose_name': 'mapRegionJumps'},
        ),
        migrations.AlterModelOptions(
            name='mapsolarsystem',
            options={'verbose_name': 'mapSolarSystems'},
        ),
        migrations.AlterModelOptions(
            name='mapsolarsystemjump',
            options={'verbose_name': 'mapSolarSystemJumps'},
        ),
        migrations.AlterModelOptions(
            name='mapuniverse',
            options={'verbose_name': 'mapUniverse'},
        ),
        migrations.AlterModelOptions(
            name='planetschematic',
            options={'verbose_name': 'planetSchematics'},
        ),
        migrations.AlterModelOptions(
            name='planetschematicspinmap',
            options={'verbose_name': 'planetSchematicsPinMap'},
        ),
        migrations.AlterModelOptions(
            name='planetschematicstypemap',
            options={'verbose_name': 'planetSchematicsTypeMap'},
        ),
        migrations.AlterModelOptions(
            name='ramactivity',
            options={'verbose_name': 'ramActivities'},
        ),
        migrations.AlterModelOptions(
            name='ramassemblylinestation',
            options={'verbose_name': 'ramAssemblyLineStations'},
        ),
        migrations.AlterModelOptions(
            name='ramassemblylinetype',
            options={'verbose_name': 'ramAssemblyLineTypes'},
        ),
        migrations.AlterModelOptions(
            name='ramassemblylinetypedetailpercategory',
            options={'verbose_name': 'ramAssemblyLineTypeDetailPerCategory'},
        ),
        migrations.AlterModelOptions(
            name='ramassemblylinetypedetailpergroup',
            options={'verbose_name': 'ramAssemblyLineTypeDetailPerGroup'},
        ),
        migrations.AlterModelOptions(
            name='raminstallationtypecontent',
            options={'verbose_name': 'ramInstallationTypeContents'},
        ),
        migrations.AlterModelOptions(
            name='staoperation',
            options={'verbose_name': 'staOperations'},
        ),
        migrations.AlterModelOptions(
            name='staoperationservice',
            options={'verbose_name': 'staOperationServices'},
        ),
        migrations.AlterModelOptions(
            name='staservice',
            options={'verbose_name': 'staServices'},
        ),
        migrations.AlterModelOptions(
            name='stastation',
            options={'verbose_name': 'staStations'},
        ),
        migrations.AlterModelOptions(
            name='stastationtype',
            options={'verbose_name': 'staStationTypes'},
        ),
        migrations.AlterModelOptions(
            name='translationtable',
            options={'verbose_name': 'translationTables'},
        ),
        migrations.AlterModelOptions(
            name='trntranslation',
            options={'verbose_name': 'trnTranslations'},
        ),
        migrations.AlterModelOptions(
            name='trntranslationcolumn',
            options={'verbose_name': 'trnTranslationColumns'},
        ),
        migrations.AlterModelOptions(
            name='trntranslationlanguage',
            options={'verbose_name': 'trnTranslationLanguages'},
        ),
        migrations.AlterModelOptions(
            name='warcombatzone',
            options={'verbose_name': 'warCombatZones'},
        ),
        migrations.AlterModelOptions(
            name='warcombatzonesystem',
            options={'verbose_name': 'warCombatZoneSystems'},
        ),
    ]
