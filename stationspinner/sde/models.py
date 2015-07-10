# This is an auto-generated Django model module.
# It was made by stationspinner's inspect_sde which has special
# seasoning for importing the SDE dumps generated for postgresql.
from django.db import models



class AgtAgentType(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'agentTypeID')
    agentType = models.TextField(blank=True)
    class Meta:
        db_table = u'agtAgentTypes'
        verbose_name = u'agtAgentTypes'


class AgtAgent(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'agentID')
    divisionID = models.SmallIntegerField(null=True, blank=True)
    corporationID = models.BigIntegerField(null=True, blank=True)
    locationID = models.BigIntegerField(null=True, blank=True)
    level = models.SmallIntegerField(null=True, blank=True)
    quality = models.SmallIntegerField(null=True, blank=True)
    agentTypeID = models.BigIntegerField(null=True, blank=True)
    isLocator = models.NullBooleanField(null=True, blank=True)
    class Meta:
        db_table = u'agtAgents'
        verbose_name = u'agtAgents'


class CertCert(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'certID')
    description = models.TextField(blank=True)
    groupid = models.BigIntegerField(null=True, blank=True)
    name = models.TextField(blank=True)
    class Meta:
        db_table = u'certCerts'
        verbose_name = u'certCerts'


class ChrAncestry(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'ancestryID')
    ancestryName = models.TextField(blank=True)
    bloodlineID = models.SmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    perception = models.SmallIntegerField(null=True, blank=True)
    willpower = models.SmallIntegerField(null=True, blank=True)
    charisma = models.SmallIntegerField(null=True, blank=True)
    memory = models.SmallIntegerField(null=True, blank=True)
    intelligence = models.SmallIntegerField(null=True, blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    shortDescription = models.TextField(blank=True)
    class Meta:
        db_table = u'chrAncestries'
        verbose_name = u'chrAncestries'


class ChrAttribute(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'attributeID')
    attributeName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    shortDescription = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    class Meta:
        db_table = u'chrAttributes'
        verbose_name = u'chrAttributes'


class ChrBloodline(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'bloodlineID')
    bloodlineName = models.TextField(blank=True)
    raceID = models.SmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    maleDescription = models.TextField(blank=True)
    femaleDescription = models.TextField(blank=True)
    shipTypeID = models.BigIntegerField(null=True, blank=True)
    corporationID = models.BigIntegerField(null=True, blank=True)
    perception = models.SmallIntegerField(null=True, blank=True)
    willpower = models.SmallIntegerField(null=True, blank=True)
    charisma = models.SmallIntegerField(null=True, blank=True)
    memory = models.SmallIntegerField(null=True, blank=True)
    intelligence = models.SmallIntegerField(null=True, blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    shortDescription = models.TextField(blank=True)
    shortMaleDescription = models.TextField(blank=True)
    shortFemaleDescription = models.TextField(blank=True)
    class Meta:
        db_table = u'chrBloodlines'
        verbose_name = u'chrBloodlines'


class ChrFaction(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'factionID')
    factionName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    raceIDs = models.BigIntegerField(null=True, blank=True)
    solarSystem = models.ForeignKey('MapSolarSystem', null=True, db_column='solarSystemID')
    corporationID = models.BigIntegerField(null=True, blank=True)
    sizeFactor = models.FloatField(null=True, blank=True)
    stationCount = models.SmallIntegerField(null=True, blank=True)
    stationSystemCount = models.SmallIntegerField(null=True, blank=True)
    militiaCorporationID = models.BigIntegerField(null=True, blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    class Meta:
        db_table = u'chrFactions'
        verbose_name = u'chrFactions'


class ChrRace(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'raceID')
    raceName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    shortDescription = models.TextField(blank=True)
    class Meta:
        db_table = u'chrRaces'
        verbose_name = u'chrRaces'


class CrpActivity(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'activityID')
    activityName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = u'crpActivities'
        verbose_name = u'crpActivities'


class CrpNPCCorporation(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'corporationID')
    size = models.CharField(max_length=1, blank=True)
    extent = models.CharField(max_length=1, blank=True)
    solarSystem = models.ForeignKey('MapSolarSystem', null=True, db_column='solarSystemID')
    investorID1 = models.BigIntegerField(null=True, blank=True)
    investorShares1 = models.SmallIntegerField(null=True, blank=True)
    investorID2 = models.BigIntegerField(null=True, blank=True)
    investorShares2 = models.SmallIntegerField(null=True, blank=True)
    investorID3 = models.BigIntegerField(null=True, blank=True)
    investorShares3 = models.SmallIntegerField(null=True, blank=True)
    investorID4 = models.BigIntegerField(null=True, blank=True)
    investorShares4 = models.SmallIntegerField(null=True, blank=True)
    friendID = models.BigIntegerField(null=True, blank=True)
    enemyID = models.BigIntegerField(null=True, blank=True)
    publicShares = models.BigIntegerField(null=True, blank=True)
    initialPrice = models.BigIntegerField(null=True, blank=True)
    minSecurity = models.FloatField(null=True, blank=True)
    scattered = models.NullBooleanField(null=True, blank=True)
    fringe = models.SmallIntegerField(null=True, blank=True)
    corridor = models.SmallIntegerField(null=True, blank=True)
    hub = models.SmallIntegerField(null=True, blank=True)
    border = models.SmallIntegerField(null=True, blank=True)
    factionID = models.BigIntegerField(null=True, blank=True)
    sizeFactor = models.FloatField(null=True, blank=True)
    stationCount = models.SmallIntegerField(null=True, blank=True)
    stationSystemCount = models.SmallIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    class Meta:
        db_table = u'crpNPCCorporations'
        verbose_name = u'crpNPCCorporations'


class CrpNPCDivision(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'divisionID')
    divisionName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    leaderType = models.TextField(blank=True)
    class Meta:
        db_table = u'crpNPCDivisions'
        verbose_name = u'crpNPCDivisions'


class DgmAttributeCategory(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'categoryID')
    categoryName = models.TextField(blank=True)
    categoryDescription = models.TextField(blank=True)
    class Meta:
        db_table = u'dgmAttributeCategories'
        verbose_name = u'dgmAttributeCategories'


class DgmAttributeType(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'attributeID')
    attributeName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    defaultValue = models.FloatField(null=True, blank=True)
    published = models.NullBooleanField(null=True, blank=True)
    displayName = models.TextField(blank=True)
    unitID = models.SmallIntegerField(null=True, blank=True)
    stackable = models.NullBooleanField(null=True, blank=True)
    highIsGood = models.NullBooleanField(null=True, blank=True)
    categoryID = models.SmallIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'dgmAttributeTypes'
        verbose_name = u'dgmAttributeTypes'


class DgmEffect(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'effectID')
    effectName = models.TextField(blank=True)
    effectCategory = models.SmallIntegerField(null=True, blank=True)
    preExpression = models.BigIntegerField(null=True, blank=True)
    postExpression = models.BigIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    guid = models.TextField(blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    isOffensive = models.NullBooleanField(null=True, blank=True)
    isAssistance = models.NullBooleanField(null=True, blank=True)
    durationAttributeID = models.SmallIntegerField(null=True, blank=True)
    trackingSpeedAttributeID = models.SmallIntegerField(null=True, blank=True)
    dischargeAttributeID = models.SmallIntegerField(null=True, blank=True)
    rangeAttributeID = models.SmallIntegerField(null=True, blank=True)
    falloffAttributeID = models.SmallIntegerField(null=True, blank=True)
    disallowAutoRepeat = models.NullBooleanField(null=True, blank=True)
    published = models.NullBooleanField(null=True, blank=True)
    displayName = models.TextField(blank=True)
    isWarpSafe = models.NullBooleanField(null=True, blank=True)
    rangeChance = models.NullBooleanField(null=True, blank=True)
    electronicChance = models.NullBooleanField(null=True, blank=True)
    propulsionChance = models.NullBooleanField(null=True, blank=True)
    distribution = models.SmallIntegerField(null=True, blank=True)
    sfxName = models.TextField(blank=True)
    npcUsageChanceAttributeID = models.SmallIntegerField(null=True, blank=True)
    npcActivationChanceAttributeID = models.SmallIntegerField(null=True, blank=True)
    fittingUsageChanceAttributeID = models.SmallIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'dgmEffects'
        verbose_name = u'dgmEffects'


class EveIcon(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'iconID')
    iconFile = models.TextField()
    description = models.TextField(blank=True)

    def to_icon_file(self):
        try:
            return '%s_64_%s.PNG' % tuple(self.iconFile.split('_')[-2:])
        except:
            return None
    
    class Meta:
        db_table = u'eveIcons'
        verbose_name = u'eveIcons'


class EveUnit(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'unitID')
    unitName = models.TextField(blank=True)
    displayName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = u'eveUnits'
        verbose_name = u'eveUnits'


class IndustryBlueprint(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'typeID')
    maxProductionLimit = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'industryBlueprints'
        verbose_name = u'industryBlueprints'


class InvCategory(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'categoryID')
    categoryName = models.TextField(blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    published = models.NullBooleanField(null=True, blank=True)
    class Meta:
        db_table = u'invCategories'
        verbose_name = u'invCategories'


class InvControlTowerResourcePurpose(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'purpose')
    purposeText = models.TextField(blank=True)
    class Meta:
        db_table = u'invControlTowerResourcePurposes'
        verbose_name = u'invControlTowerResourcePurposes'


class InvFlag(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'flagID')
    flagName = models.TextField(blank=True)
    flagText = models.TextField(blank=True)
    orderID = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'invFlags'
        verbose_name = u'invFlags'


class InvGroup(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'groupID')
    categoryID = models.BigIntegerField(null=True, blank=True)
    groupName = models.TextField(blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    useBasePrice = models.NullBooleanField(null=True, blank=True)
    anchored = models.NullBooleanField(null=True, blank=True)
    anchorable = models.NullBooleanField(null=True, blank=True)
    fittableNonSingleton = models.NullBooleanField(null=True, blank=True)
    published = models.NullBooleanField(null=True, blank=True)
    class Meta:
        db_table = u'invGroups'
        verbose_name = u'invGroups'


class InvItem(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'itemID')
    typeID = models.BigIntegerField()
    ownerID = models.BigIntegerField()
    locationID = models.BigIntegerField()
    flagID = models.SmallIntegerField()
    quantity = models.BigIntegerField()
    class Meta:
        db_table = u'invItems'
        verbose_name = u'invItems'


class InvMarketGroupManager(models.Manager):
    def get_hierarchy(self, max_depth=None):
        def group_recurse(group, depth, max_depth):
            if depth == max_depth:
                children = None
            else:
                children = [group_recurse(child, depth+1, max_depth) for child in self.filter(parentGroup=group)]
            if group.icon:
                icon = group.icon.to_icon_file()
            else:
                icon = None
            tree = {
                "marketGroupName": group.marketGroupName,
                "marketGroupID": group.pk,
                "icon": icon,
                "children": children
            }
            return tree

        return [group_recurse(group, 0, max_depth) for group in self.filter(parentGroup=None,
                                                              pk__lt=35000)]



class InvMarketGroup(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'marketGroupID')
    parentGroup = models.ForeignKey('InvMarketGroup', null=True, db_column='parentGroupID')
    marketGroupName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    hasTypes = models.NullBooleanField(null=True, blank=True)

    objects = InvMarketGroupManager()

    def get_children(self):
        return InvMarketGroup.objects.filter(parentGroupID=self.pk)

    class Meta:
        db_table = u'invMarketGroups'
        verbose_name = u'invMarketGroups'


class InvMetaGroup(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'metaGroupID')
    metaGroupName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    class Meta:
        db_table = u'invMetaGroups'
        verbose_name = u'invMetaGroups'


class InvMetaType(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'typeID')
    parentTypeID = models.BigIntegerField(null=True, blank=True)
    metaGroupID = models.SmallIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'invMetaTypes'
        verbose_name = u'invMetaTypes'


class InvName(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'itemID')
    itemName = models.TextField()
    class Meta:
        db_table = u'invNames'
        verbose_name = u'invNames'


class InvPosition(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'itemID')
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    yaw = models.FloatField(null=True, blank=True)
    pitch = models.FloatField(null=True, blank=True)
    roll = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'invPositions'
        verbose_name = u'invPositions'


class InvType(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'typeID')
    groupID = models.BigIntegerField(null=True, blank=True)
    typeName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    mass = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    capacity = models.FloatField(null=True, blank=True)
    portionSize = models.BigIntegerField(null=True, blank=True)
    raceID = models.SmallIntegerField(null=True, blank=True)
    basePrice = models.DecimalField(null=True, max_digits=19, decimal_places=4, blank=True)
    published = models.NullBooleanField(null=True, blank=True)
    marketGroupID = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = u'invTypes'
        verbose_name = u'invTypes'


class InvUniqueName(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'itemID')
    itemName = models.TextField(unique=True)
    groupID = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'invUniqueNames'
        verbose_name = u'invUniqueNames'


class MapCelestialStatistic(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'celestialID')
    temperature = models.FloatField(null=True, blank=True)
    spectralClass = models.TextField(blank=True)
    luminosity = models.FloatField(null=True, blank=True)
    age = models.FloatField(null=True, blank=True)
    life = models.FloatField(null=True, blank=True)
    orbitRadius = models.FloatField(null=True, blank=True)
    eccentricity = models.FloatField(null=True, blank=True)
    massDust = models.FloatField(null=True, blank=True)
    massGas = models.FloatField(null=True, blank=True)
    fragmented = models.BigIntegerField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True)
    surfaceGravity = models.FloatField(null=True, blank=True)
    escapeVelocity = models.FloatField(null=True, blank=True)
    orbitPeriod = models.FloatField(null=True, blank=True)
    rotationRate = models.FloatField(null=True, blank=True)
    locked = models.BigIntegerField(null=True, blank=True)
    pressure = models.BigIntegerField(null=True, blank=True)
    radius = models.BigIntegerField(null=True, blank=True)
    mass = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mapCelestialStatistics'
        verbose_name = u'mapCelestialStatistics'


class MapConstellation(models.Model):
    region = models.ForeignKey('MapRegion', null=True, db_column='regionID')
    id = models.BigIntegerField(primary_key=True, db_column=u'constellationID')
    constellationName = models.TextField(blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    xMin = models.FloatField(null=True, blank=True)
    xMax = models.FloatField(null=True, blank=True)
    yMin = models.FloatField(null=True, blank=True)
    yMax = models.FloatField(null=True, blank=True)
    zMin = models.FloatField(null=True, blank=True)
    zMax = models.FloatField(null=True, blank=True)
    factionID = models.BigIntegerField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'mapConstellations'
        verbose_name = u'mapConstellations'


class MapJump(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'stargateID')
    destinationID = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mapJumps'
        verbose_name = u'mapJumps'


class MapLandmark(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'landmarkID')
    landmarkName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    locationID = models.BigIntegerField(null=True, blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    icon = models.ForeignKey('EveIcon', null=True, db_column='iconID')
    class Meta:
        db_table = u'mapLandmarks'
        verbose_name = u'mapLandmarks'


class MapLocationScene(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'locationID')
    graphicID = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mapLocationScenes'
        verbose_name = u'mapLocationScenes'


class MapLocationWormholeClass(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'locationID')
    wormholeClassID = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mapLocationWormholeClasses'
        verbose_name = u'mapLocationWormholeClasses'


class MapRegion(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'regionID')
    regionName = models.TextField(blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    xMin = models.FloatField(null=True, blank=True)
    xMax = models.FloatField(null=True, blank=True)
    yMin = models.FloatField(null=True, blank=True)
    yMax = models.FloatField(null=True, blank=True)
    zMin = models.FloatField(null=True, blank=True)
    zMax = models.FloatField(null=True, blank=True)
    factionID = models.BigIntegerField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'mapRegions'
        verbose_name = u'mapRegions'


class MapSolarSystem(models.Model):
    region = models.ForeignKey('MapRegion', null=True, db_column='regionID')
    constellationID = models.BigIntegerField(null=True, blank=True)
    id = models.BigIntegerField(primary_key=True, db_column=u'solarSystemID')
    solarSystemName = models.TextField(blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    xMin = models.FloatField(null=True, blank=True)
    xMax = models.FloatField(null=True, blank=True)
    yMin = models.FloatField(null=True, blank=True)
    yMax = models.FloatField(null=True, blank=True)
    zMin = models.FloatField(null=True, blank=True)
    zMax = models.FloatField(null=True, blank=True)
    luminosity = models.FloatField(null=True, blank=True)
    border = models.BigIntegerField(null=True, blank=True)
    fringe = models.BigIntegerField(null=True, blank=True)
    corridor = models.BigIntegerField(null=True, blank=True)
    hub = models.BigIntegerField(null=True, blank=True)
    international = models.BigIntegerField(null=True, blank=True)
    regional = models.BigIntegerField(null=True, blank=True)
    constellation = models.BigIntegerField(null=True, blank=True)
    security = models.FloatField(null=True, blank=True)
    factionID = models.BigIntegerField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    sunTypeID = models.BigIntegerField(null=True, blank=True)
    securityClass = models.TextField(blank=True)

    class Meta:
        db_table = u'mapSolarSystems'
        verbose_name = u'mapSolarSystems'


class MapUniverse(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'universeID')
    universeName = models.TextField(blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    xMin = models.FloatField(null=True, blank=True)
    xMax = models.FloatField(null=True, blank=True)
    yMin = models.FloatField(null=True, blank=True)
    yMax = models.FloatField(null=True, blank=True)
    zMin = models.FloatField(null=True, blank=True)
    zMax = models.FloatField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'mapUniverse'
        verbose_name = u'mapUniverse'


class PlanetSchematic(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'schematicID')
    schematicName = models.TextField(blank=True)
    cycleTime = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'planetSchematics'
        verbose_name = u'planetSchematics'


class RamActivity(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'activityID')
    activityName = models.TextField(blank=True)
    iconNo = models.TextField(blank=True)
    description = models.TextField(blank=True)
    published = models.NullBooleanField(null=True, blank=True)
    class Meta:
        db_table = u'ramActivities'
        verbose_name = u'ramActivities'


class RamAssemblyLineType(models.Model):
    id = models.SmallIntegerField(primary_key=True, db_column=u'assemblyLineTypeID')
    assemblyLineTypeName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    baseTimeMultiplier = models.FloatField(null=True, blank=True)
    baseMaterialMultiplier = models.FloatField(null=True, blank=True)
    baseCostMultiplier = models.FloatField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    activityID = models.SmallIntegerField(null=True, blank=True)
    minCostPerHour = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'ramAssemblyLineTypes'
        verbose_name = u'ramAssemblyLineTypes'


class StaOperation(models.Model):
    activityID = models.SmallIntegerField(null=True, blank=True)
    id = models.SmallIntegerField(primary_key=True, db_column=u'operationID')
    operationName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    fringe = models.SmallIntegerField(null=True, blank=True)
    corridor = models.SmallIntegerField(null=True, blank=True)
    hub = models.SmallIntegerField(null=True, blank=True)
    border = models.SmallIntegerField(null=True, blank=True)
    ratio = models.SmallIntegerField(null=True, blank=True)
    caldariStationTypeID = models.BigIntegerField(null=True, blank=True)
    minmatarStationTypeID = models.BigIntegerField(null=True, blank=True)
    amarrStationTypeID = models.BigIntegerField(null=True, blank=True)
    gallenteStationTypeID = models.BigIntegerField(null=True, blank=True)
    joveStationTypeID = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'staOperations'
        verbose_name = u'staOperations'


class StaService(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'serviceID')
    serviceName = models.TextField(blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = u'staServices'
        verbose_name = u'staServices'


class StaStationType(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'stationTypeID')
    dockEntryX = models.FloatField(null=True, blank=True)
    dockEntryY = models.FloatField(null=True, blank=True)
    dockEntryZ = models.FloatField(null=True, blank=True)
    dockOrientationX = models.FloatField(null=True, blank=True)
    dockOrientationY = models.FloatField(null=True, blank=True)
    dockOrientationZ = models.FloatField(null=True, blank=True)
    operationID = models.SmallIntegerField(null=True, blank=True)
    officeSlots = models.SmallIntegerField(null=True, blank=True)
    reprocessingEfficiency = models.FloatField(null=True, blank=True)
    conquerable = models.NullBooleanField(null=True, blank=True)
    class Meta:
        db_table = u'staStationTypes'
        verbose_name = u'staStationTypes'


class StaStation(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'stationID')
    security = models.SmallIntegerField(null=True, blank=True)
    dockingCostPerVolume = models.FloatField(null=True, blank=True)
    maxShipVolumeDockable = models.FloatField(null=True, blank=True)
    officeRentalCost = models.BigIntegerField(null=True, blank=True)
    operationID = models.SmallIntegerField(null=True, blank=True)
    stationType = models.ForeignKey('StaStationType', null=True, db_column='stationTypeID')
    corporationID = models.BigIntegerField(null=True, blank=True)
    solarSystem = models.ForeignKey('MapSolarSystem', null=True, db_column='solarSystemID')
    constellation = models.ForeignKey('MapConstellation', null=True, db_column='constellationID')
    region = models.ForeignKey('MapRegion', null=True, db_column='regionID')
    stationName = models.TextField(blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    reprocessingEfficiency = models.FloatField(null=True, blank=True)
    reprocessingStationsTake = models.FloatField(null=True, blank=True)
    reprocessingHangarFlag = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = u'staStations'
        verbose_name = u'staStations'


class TrnTranslationColumn(models.Model):
    tcGroupID = models.SmallIntegerField(null=True, blank=True)
    id = models.SmallIntegerField(primary_key=True, db_column=u'tcID')
    tableName = models.TextField()
    columnName = models.TextField()
    masterID = models.TextField(blank=True)
    class Meta:
        db_table = u'trnTranslationColumns'
        verbose_name = u'trnTranslationColumns'


class TrnTranslationLanguage(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'numericLanguageID')
    languageID = models.TextField(blank=True)
    languageName = models.TextField(blank=True)
    class Meta:
        db_table = u'trnTranslationLanguages'
        verbose_name = u'trnTranslationLanguages'


class WarCombatZoneSystem(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'solarSystemID')
    combatZoneID = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'warCombatZoneSystems'
        verbose_name = u'warCombatZoneSystems'


class WarCombatZone(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'combatZoneID')
    combatZoneName = models.TextField(blank=True)
    factionID = models.BigIntegerField(null=True, blank=True)
    centerSystemID = models.BigIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = u'warCombatZones'
        verbose_name = u'warCombatZones'


class TrnTranslation(models.Model):
    tcID = models.SmallIntegerField()
    keyID = models.BigIntegerField()
    languageID = models.TextField()
    text = models.TextField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'trnTranslations'
        verbose_name = u'trnTranslations'


class AgtResearchAgent(models.Model):
    agentID = models.BigIntegerField()
    typeID = models.BigIntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'agtResearchAgents'
        verbose_name = u'agtResearchAgents'


class CertMastery(models.Model):
    typeID = models.BigIntegerField(null=True, blank=True)
    masteryLevel = models.BigIntegerField(null=True, blank=True)
    certID = models.BigIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'certMasteries'
        verbose_name = u'certMasteries'


class CrpNPCCorporationDivision(models.Model):
    corporationID = models.BigIntegerField()
    divisionID = models.SmallIntegerField()
    size = models.SmallIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'crpNPCCorporationDivisions'
        verbose_name = u'crpNPCCorporationDivisions'


class CertSkill(models.Model):
    certID = models.BigIntegerField(null=True, blank=True)
    skillID = models.BigIntegerField(null=True, blank=True)
    certLevelInt = models.BigIntegerField(null=True, blank=True)
    skillLevel = models.BigIntegerField(null=True, blank=True)
    certLevelText = models.TextField(blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'certSkills'
        verbose_name = u'certSkills'


class CrpNPCCorporationResearchField(models.Model):
    skillID = models.BigIntegerField()
    corporationID = models.BigIntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'crpNPCCorporationResearchFields'
        verbose_name = u'crpNPCCorporationResearchFields'


class CrpNPCCorporationTrade(models.Model):
    corporationID = models.BigIntegerField()
    typeID = models.BigIntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'crpNPCCorporationTrades'
        verbose_name = u'crpNPCCorporationTrades'


class DgmTypeAttribute(models.Model):
    typeID = models.BigIntegerField()
    attributeID = models.SmallIntegerField()
    valueInt = models.BigIntegerField(null=True, blank=True)
    valueFloat = models.FloatField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'dgmTypeAttributes'
        verbose_name = u'dgmTypeAttributes'


class DgmTypeEffect(models.Model):
    typeID = models.BigIntegerField()
    effectID = models.SmallIntegerField()
    isDefault = models.NullBooleanField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'dgmTypeEffects'
        verbose_name = u'dgmTypeEffects'


class IndustryActivity(models.Model):
    typeID = models.BigIntegerField()
    time = models.BigIntegerField(null=True, blank=True)
    activityID = models.BigIntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'industryActivity'
        verbose_name = u'industryActivity'


class IndustryActivityMaterial(models.Model):
    typeID = models.BigIntegerField(null=True, blank=True)
    activityID = models.BigIntegerField(null=True, blank=True)
    materialTypeID = models.BigIntegerField(null=True, blank=True)
    quantity = models.BigIntegerField(null=True, blank=True)
    consume = models.SmallIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'industryActivityMaterials'
        verbose_name = u'industryActivityMaterials'


class IndustryActivityProbability(models.Model):
    typeID = models.BigIntegerField(null=True, blank=True)
    activityID = models.BigIntegerField(null=True, blank=True)
    productTypeID = models.BigIntegerField(null=True, blank=True)
    probability = models.DecimalField(null=True, max_digits=3, decimal_places=2, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'industryActivityProbabilities'
        verbose_name = u'industryActivityProbabilities'


class IndustryActivityProduct(models.Model):
    typeID = models.BigIntegerField(null=True, blank=True)
    activityID = models.BigIntegerField(null=True, blank=True)
    productTypeID = models.BigIntegerField(null=True, blank=True)
    quantity = models.BigIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'industryActivityProducts'
        verbose_name = u'industryActivityProducts'


class IndustryActivityRace(models.Model):
    typeID = models.BigIntegerField(null=True, blank=True)
    activityID = models.SmallIntegerField(null=True, blank=True)
    productTypeID = models.BigIntegerField(null=True, blank=True)
    raceID = models.SmallIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'industryActivityRaces'
        verbose_name = u'industryActivityRaces'


class IndustryActivitySkill(models.Model):
    typeID = models.BigIntegerField(null=True, blank=True)
    activityID = models.BigIntegerField(null=True, blank=True)
    skillID = models.BigIntegerField(null=True, blank=True)
    level = models.BigIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'industryActivitySkills'
        verbose_name = u'industryActivitySkills'


class InvContrabandType(models.Model):
    factionID = models.BigIntegerField()
    typeID = models.BigIntegerField()
    standingLoss = models.FloatField(null=True, blank=True)
    confiscateMinSec = models.FloatField(null=True, blank=True)
    fineByValue = models.FloatField(null=True, blank=True)
    attackMinSec = models.FloatField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'invContrabandTypes'
        verbose_name = u'invContrabandTypes'


class InvControlTowerResource(models.Model):
    controlTowerTypeID = models.BigIntegerField()
    resourceTypeID = models.BigIntegerField()
    purpose = models.SmallIntegerField(null=True, blank=True)
    quantity = models.BigIntegerField(null=True, blank=True)
    minSecurityLevel = models.FloatField(null=True, blank=True)
    factionID = models.BigIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'invControlTowerResources'
        verbose_name = u'invControlTowerResources'


class InvTrait(models.Model):
    typeID = models.BigIntegerField(null=True, blank=True)
    skillID = models.BigIntegerField(null=True, blank=True)
    bonus = models.FloatField(null=True, blank=True)
    bonusText = models.TextField(blank=True)
    unitID = models.BigIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'invTraits'
        verbose_name = u'invTraits'


class InvTypeMaterial(models.Model):
    typeID = models.BigIntegerField()
    materialTypeID = models.BigIntegerField()
    quantity = models.BigIntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'invTypeMaterials'
        verbose_name = u'invTypeMaterials'


class InvTypeReaction(models.Model):
    reactionTypeID = models.BigIntegerField()
    input = models.NullBooleanField()
    typeID = models.BigIntegerField()
    quantity = models.SmallIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'invTypeReactions'
        verbose_name = u'invTypeReactions'


class MapConstellationJump(models.Model):
    fromRegionID = models.BigIntegerField(null=True, blank=True)
    fromConstellationID = models.BigIntegerField()
    toConstellationID = models.BigIntegerField()
    toRegionID = models.BigIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'mapConstellationJumps'
        verbose_name = u'mapConstellationJumps'


class MapRegionJump(models.Model):
    fromRegionID = models.BigIntegerField()
    toRegionID = models.BigIntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'mapRegionJumps'
        verbose_name = u'mapRegionJumps'


class MapSolarSystemJump(models.Model):
    fromRegionID = models.BigIntegerField(null=True, blank=True)
    fromConstellationID = models.BigIntegerField(null=True, blank=True)
    fromSolarSystemID = models.BigIntegerField()
    toSolarSystemID = models.BigIntegerField()
    toConstellationID = models.BigIntegerField(null=True, blank=True)
    toRegionID = models.BigIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'mapSolarSystemJumps'
        verbose_name = u'mapSolarSystemJumps'


class PlanetSchematicsPinMap(models.Model):
    schematicID = models.SmallIntegerField()
    pinTypeID = models.BigIntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'planetSchematicsPinMap'
        verbose_name = u'planetSchematicsPinMap'


class PlanetSchematicsTypeMap(models.Model):
    schematicID = models.SmallIntegerField()
    typeID = models.BigIntegerField()
    quantity = models.SmallIntegerField(null=True, blank=True)
    isInput = models.NullBooleanField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'planetSchematicsTypeMap'
        verbose_name = u'planetSchematicsTypeMap'


class RamAssemblyLineStation(models.Model):
    stationID = models.BigIntegerField()
    assemblyLineTypeID = models.SmallIntegerField()
    quantity = models.SmallIntegerField(null=True, blank=True)
    stationTypeID = models.BigIntegerField(null=True, blank=True)
    ownerID = models.BigIntegerField(null=True, blank=True)
    solarSystem = models.ForeignKey('MapSolarSystem', null=True, db_column='solarSystemID')
    region = models.ForeignKey('MapRegion', null=True, db_column='regionID')
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'ramAssemblyLineStations'
        verbose_name = u'ramAssemblyLineStations'


class RamAssemblyLineTypeDetailPerCategory(models.Model):
    assemblyLineTypeID = models.SmallIntegerField()
    categoryID = models.BigIntegerField()
    timeMultiplier = models.FloatField(null=True, blank=True)
    materialMultiplier = models.FloatField(null=True, blank=True)
    costMultiplier = models.FloatField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'ramAssemblyLineTypeDetailPerCategory'
        verbose_name = u'ramAssemblyLineTypeDetailPerCategory'


class RamAssemblyLineTypeDetailPerGroup(models.Model):
    assemblyLineTypeID = models.SmallIntegerField()
    groupID = models.BigIntegerField()
    timeMultiplier = models.FloatField(null=True, blank=True)
    materialMultiplier = models.FloatField(null=True, blank=True)
    costMultiplier = models.FloatField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'ramAssemblyLineTypeDetailPerGroup'
        verbose_name = u'ramAssemblyLineTypeDetailPerGroup'


class RamInstallationTypeContent(models.Model):
    installationTypeID = models.BigIntegerField()
    assemblyLineTypeID = models.SmallIntegerField()
    quantity = models.SmallIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'ramInstallationTypeContents'
        verbose_name = u'ramInstallationTypeContents'


class StaOperationService(models.Model):
    operationID = models.SmallIntegerField()
    serviceID = models.BigIntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'staOperationServices'
        verbose_name = u'staOperationServices'


class TranslationTable(models.Model):
    sourceTable = models.TextField()
    destinationTable = models.TextField(blank=True)
    translatedKey = models.TextField()
    tcGroupID = models.BigIntegerField(null=True, blank=True)
    tcID = models.BigIntegerField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'translationTables'
        verbose_name = u'translationTables'


class MapDenormalize(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column=u'itemID')
    type = models.ForeignKey(InvType, null=True, db_column='typeID', related_name='mapdenormalize_type')
    group = models.ForeignKey(InvGroup, null=True, db_column='groupID', related_name='mapdenormalize_group')
    solarSystem = models.ForeignKey(MapSolarSystem, null=True, db_column='solarSystemID', related_name='mapdenormalize_solarSystem')
    constellation = models.ForeignKey(MapConstellation, null=True, db_column='constellationID', related_name='mapdenormalize_constellation')
    region = models.ForeignKey(MapRegion, null=True, db_column='regionID', related_name='mapdenormalize_region')
    orbit = models.ForeignKey('self', null=True, db_column='orbitID', related_name='mapdenormalize_orbit')
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    itemName = models.TextField(blank=True)
    security = models.FloatField(null=True, blank=True)
    celestialIndex = models.BigIntegerField(null=True, blank=True)
    orbitIndex = models.BigIntegerField(null=True, blank=True)

    def regionName(self):
        return self.region.regionName

    def solarSystemName(self):
        if self.solarSystem:
            return self.solarSystem.solarSystemName
        else:
            return None

    def regionID(self):
        if self.region:
            return self.region.pk
        else:
            # Hardcoding this to save a lookup. Hopefully it never chances :)
            if self.type == 3:
                return self.pk

    def solarSystemID(self):
        if self.solarSystem:
            return self.solarSystem.pk
        else:
            if self.type == 5:
                return self.pk


    class Meta:
        db_table = u'mapDenormalize'
        verbose_name = u'mapDenormalize'