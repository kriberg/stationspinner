from decimal import Decimal
from django.db import models
from django.contrib.postgres.fields import JSONField
from stationspinner.accounting.models import APIKey, Capsuler
from stationspinner.universe.models import EveName
from stationspinner.libs import fields as custom
from django.db.models.signals import post_save
from django.dispatch import receiver
from stationspinner.celery import app
from stationspinner.libs.pragma import get_item_packaged_volume, \
    PACKAGED_VOLUME, UnknownPackagedItem, get_location, get_location_name, \
    get_location_regionID, get_location_regionName, \
    get_location_solarSystemID, get_location_solarSystemName
from stationspinner.sde.models import InvType
from celery.utils.log import get_task_logger
from django.db import connections
log = get_task_logger(__name__)


class CorporationSheetManager(models.Manager):
    def filter_valid(self, corporationIDs, capsuler):
        valid = self.filter(pk__in=corporationIDs, owner=capsuler).values_list('corporationID', flat=True)
        invalid = set(corporationIDs) - set(valid)
        return valid, invalid


class CorporationSheet(models.Model):
    owner_key = models.ForeignKey(APIKey)
    owner = models.ForeignKey(Capsuler)
    enabled = models.BooleanField(default=False)

    corporationID = models.IntegerField(primary_key=True)
    corporationName = models.CharField(max_length=255)
    allianceID = models.IntegerField(null=True)
    allianceName = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, default='')
    memberLimit = models.IntegerField(null=True)
    taxRate = models.IntegerField()
    factionID = models.IntegerField(null=True, default=0)
    ceoName = models.CharField(max_length=255)
    ceoID = models.IntegerField()
    stationName = models.CharField(max_length=255)
    stationID = models.IntegerField()
    ticker = models.CharField(max_length=10)
    memberCount = models.IntegerField(default=1)
    shares = models.IntegerField(default=1)
    url = models.CharField(max_length=255, blank=True, default='')

    objects = CorporationSheetManager()

    def update_from_api(self, sheet, handler):
        handler.autoparse(sheet, self)
        self.enabled = True
        self.save()
        EveName.objects.register(self.pk, self.corporationName)
        handler.autoparse_list(sheet.divisions,
                              Division,
                              unique_together=('accountKey',),
                              extra_selectors={'owner': self},
                              owner=self,
                              pre_save=True)

        handler.autoparse_list(sheet.walletDivisions,
                              WalletDivision,
                              unique_together=('accountKey',),
                              extra_selectors={'owner': self},
                              owner=self,
                              pre_save=True)

    def __unicode__(self):
        return self.corporationName

class Shareholder(models.Model):
    HOLDER_TYPES = (
        ('Corporation', 'Corporation'),
        ('Character', 'Character'),
    )
    holder_type = models.CharField(max_length=11, choices=HOLDER_TYPES)
    shareholderID = models.BigIntegerField()
    shareholderName = models.CharField(max_length=255)
    shareholderCorporationID = models.BigIntegerField(null=True)
    shareholderCorporationName = models.CharField(max_length=255, null=True)
    shares = models.IntegerField(default=1)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'shareholderID', 'holder_type')


class MemberTracking(models.Model):
    characterID = models.IntegerField()
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, default='')
    startDateTime = custom.DateTimeField()
    logonDateTime = custom.DateTimeField(null=True)
    logoffDateTime = custom.DateTimeField()
    locationID = models.IntegerField()
    location = models.CharField(max_length=255)
    shipTypeID = models.IntegerField()
    shipType = models.CharField(max_length=255, blank=True, default='')
    roles = models.BigIntegerField(default=0)
    grantableRoles = models.BigIntegerField(default=0)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'characterID')


class MemberMedal(models.Model):
    medalID = models.BigIntegerField()
    characterID = models.BigIntegerField()
    reason = models.TextField(blank=True, default='')
    status = models.CharField(max_length=10)
    issuerID = models.BigIntegerField()
    issued = custom.DateTimeField()

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'medalID', 'characterID')


class Medal(models.Model):
    medalID = models.BigIntegerField()
    title = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, default='')
    created = custom.DateTimeField()
    creatorID = models.IntegerField()

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('medalID', 'owner')


class Starbase(models.Model):
    STATES = {
        0: 	'Unanchored',           # Also unanchoring? Has valid stateTimestamp.
                                    # Note that moonID is zero for unanchored Towers, but
                                    # locationID will still yield the solar system ID.
        1: 	'Anchored/Offline',     # No time information stored.
        2: 	'Onlining', 	        # Will be online at time = onlineTimestamp.
        3: 	'Reinforced',           # Until time = stateTimestamp.
        4: 	'Online' 	            # Continuously since time = onlineTimestamp.
    }

    itemID = models.BigIntegerField()
    typeID = models.IntegerField()
    standingOwnerID = models.IntegerField()
    stateTimestamp = custom.DateTimeField()
    state = models.IntegerField()
    onlineTimestamp = custom.DateTimeField()
    locationID = models.IntegerField(null=True)
    moonID = models.IntegerField(null=True)

    # General settings
    # They store access restrictions to the POS facilities on 2 bits:
    #     0: 'Starbase Config',
    #     1: 'Starbase Fuel Tech',
    #     2: 'Corporation Members',
    #     3: 'Alliance Members',
    # usageFlags
    #     access restrictions to the POS fuel bay are encoded in this 4 bit field.
    #     example: if usageFlags == 9 == 0b1001   -->   10    01
    #                                                  view  take
    #         0b10 == 2 --> 'Corporation Members' can view
    #         0b01 == 1 --> 'Starbase Fuel Tech' can take
    # deployFlags
    #     access restrictions to who is able to operate this POS are encoded in this 8 bit field.
    #     example: if usageFlags == 68 == 0b01000100  -->   01       00       01      00
    #                                                     anchor  unanchor  online  offline
    #         0b01 == 1 --> 'Starbase Fuel Tech' can anchor
    #         0b00 == 0 --> 'Starbase Config' can unanchor
    #         0b01 == 1 --> 'Starbase Fuel Tech' can online
    #         0b00 == 0 --> 'Starbase Config' can offline
    general_settings = JSONField(default={}, blank=True)

    # Combat settings
    combat_settings = JSONField(default={}, blank=True)

    owner = models.ForeignKey(CorporationSheet)

    def parse_general_settings(self, starbase_details):
        self.general_settings = {
            'usageFlags': getattr(starbase_details.generalSettings, 'usageFlags', 0),
            'deployFlags': getattr(starbase_details.generalSettings, 'deployFlags', 0),
            'allowCorporationMembers': getattr(starbase_details.generalSettings, 'allowCorporationMembers', 0),
            'allowAllianceMembers': getattr(starbase_details.generalSettings, 'allowAllianceMembers', 0),
        }
    def parse_combat_settings(self, starbase_details):
        self.combat_settings = {
            'useStandingsFrom': {
                'ownerID': starbase_details.combatSettings.useStandingsFrom.ownerID
            },
            'onStandingDrop': {
                'standing': starbase_details.combatSettings.onStandingDrop.standing
            },
            'onStatusDrop': {
                'enabled': starbase_details.combatSettings.onStatusDrop.enabled,
                'standing': starbase_details.combatSettings.onStatusDrop.enabled
            },
            'onAggression': {
                'enabled': starbase_details.combatSettings.onAggression.enabled
            },
            'onCorporationWar': {
                'enabled': starbase_details.combatSettings.onCorporationWar.enabled
            }
        }

    def get_state(self):
        return self.STATES[self.state]

    def get_fuel(self):
        return StarbaseFuel.objects.filter(starbase=self)

    class Meta(object):
        unique_together = ('itemID', 'owner')


class StarbaseFuel(models.Model):
    starbase = models.ForeignKey(Starbase)
    typeID = models.IntegerField()
    quantity = models.IntegerField()

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'starbase', 'typeID')


class Outpost(models.Model):
    stationID = models.BigIntegerField(primary_key=True)
    stationName = models.CharField(max_length=255)
    reprocessingEfficiency = models.DecimalField(max_digits=30, decimal_places=10, default=0.0)
    reprocessingStationTake = models.DecimalField(max_digits=30, decimal_places=10, default=0.0)
    officeRentalCost = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    dockingCostPerShipColume = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)
    standingOwnerID = models.BigIntegerField()
    ownerID = models.BigIntegerField()
    solarSystemID = models.IntegerField()
    stationTypeID = models.IntegerField()

    owner = models.ForeignKey(CorporationSheet)

    def get_services(self):
        return OutpostService.objects.filter(stationID=self.stationID,
                                             owner=self.owner)

    class Meta(object):
        unique_together = ('stationID', 'owner')


class OutpostService(models.Model):
    stationID = models.BigIntegerField()
    serviceName = models.CharField(max_length=255)
    minStanding = models.DecimalField(max_digits=5, decimal_places=2)
    surchargePerBadStanding = models.IntegerField()
    discountPerGoodStanding = models.IntegerField()

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('stationID', 'serviceName', 'owner')


class Blueprint(models.Model):
    itemID = models.BigIntegerField()
    typeID = models.IntegerField()
    runs = models.IntegerField()
    flagID = models.IntegerField()
    timeEfficiency = models.IntegerField()
    materialEfficiency = models.IntegerField()
    typeName = models.CharField(max_length=255)
    locationID = models.BigIntegerField()
    quantity = models.IntegerField()

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('itemID', 'owner')


class IndustryJob(models.Model):
    status = models.IntegerField(null=True)
    startDate = custom.DateTimeField()
    endDate = custom.DateTimeField()
    probability = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    blueprintTypeName = models.CharField(max_length=255, blank=True, null=True)
    runs = models.IntegerField(null=True)
    outputLocationID = models.BigIntegerField()
    activityID = models.IntegerField()
    cost = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    blueprintTypeID = models.IntegerField(null=True)
    timeInSeconds = models.IntegerField()
    productTypeID = models.IntegerField(null=True)
    completedDate = custom.DateTimeField(null=True)
    completedCharacterID = models.BigIntegerField(null=True)
    installerName = models.CharField(max_length=255)
    installerID = models.BigIntegerField()
    facilityID = models.BigIntegerField()
    pauseDate = custom.DateTimeField(null=True)
    solarSystemName = models.CharField(max_length=255)
    stationID = models.BigIntegerField(null=True)
    jobID = models.BigIntegerField()
    teamID = models.IntegerField(null=True)
    productTypeName = models.CharField(max_length=255, blank=True, null=True)
    blueprintLocationID = models.BigIntegerField(null=True)
    blueprintID = models.BigIntegerField(null=True)
    solarSystemID = models.IntegerField()
    licensedRuns = models.IntegerField(null=True)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'jobID')


class IndustryJobHistory(models.Model):
    status = models.IntegerField(null=True)
    startDate = custom.DateTimeField()
    endDate = custom.DateTimeField()
    probability = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    blueprintTypeName = models.CharField(max_length=255, blank=True, null=True)
    runs = models.IntegerField(null=True)
    outputLocationID = models.BigIntegerField()
    activityID = models.IntegerField()
    cost = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    blueprintTypeID = models.BigIntegerField(null=True)
    timeInSeconds = models.IntegerField()
    productTypeID = models.IntegerField(null=True)
    completedDate = custom.DateTimeField(null=True)
    completedCharacterID = models.BigIntegerField(null=True)
    installerName = models.CharField(max_length=255)
    installerID = models.BigIntegerField()
    facilityID = models.BigIntegerField()
    pauseDate = custom.DateTimeField(null=True)
    solarSystemName = models.CharField(max_length=255)
    stationID = models.BigIntegerField(null=True)
    jobID = models.BigIntegerField()
    teamID = models.IntegerField(null=True)
    productTypeName = models.CharField(max_length=255, blank=True, null=True)
    blueprintLocationID = models.BigIntegerField(null=True)
    blueprintID = models.BigIntegerField(null=True)
    solarSystemID = models.IntegerField()
    licensedRuns = models.IntegerField(null=True)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'jobID')


class WalletTransaction(models.Model):
    typeID = models.IntegerField()
    clientTypeID = models.IntegerField()
    transactionFor = models.CharField(max_length=11)
    price = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    clientID = models.BigIntegerField()
    journalTransactionID = models.BigIntegerField()
    typeName = models.CharField(max_length=255, blank=True, default='')
    stationID = models.BigIntegerField()
    stationName = models.CharField(max_length=255, blank=True, default='')
    transactionID = models.BigIntegerField(null=True)
    quantity = models.IntegerField()
    transactionDateTime = custom.DateTimeField()
    clientName = models.CharField(max_length=255, blank=True, default='')
    transactionType = models.CharField(max_length=4)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'transactionID')

class WalletJournal(models.Model):
    taxReceiverID = models.CharField(max_length=255, blank=True, null=True)
    argName1 = models.CharField(max_length=255, blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    date = custom.DateTimeField()
    refTypeID = models.IntegerField(null=True)
    refID = models.BigIntegerField(db_index=True)
    ownerID2 = models.IntegerField(null=True)
    taxAmount = models.CharField(max_length=255, blank=True, null=True)
    ownerID1 = models.IntegerField(null=True)
    argID1 = models.IntegerField(null=True)
    owner1TypeID = models.IntegerField(null=True)
    ownerName2 = models.CharField(max_length=255, blank=True, null=True)
    owner2TypeID = models.IntegerField(null=True)
    ownerName1 = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    balance = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    accountKey = models.IntegerField()

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'refID', 'accountKey')


class Contact(models.Model):
    CONTACT_LIST_TYPES = (
        ('Corporate', 'Corporate'),
        ('Alliance', 'Alliance')
    )
    standing = models.DecimalField(max_digits=6, decimal_places=3)
    contactID = models.BigIntegerField()
    contactName = models.CharField(max_length=255)
    contactTypeID = models.IntegerField()
    listType = models.CharField(max_length=20, choices=CONTACT_LIST_TYPES)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'contactID', 'listType')


class AssetList(models.Model):
    items = JSONField()
    retrieved = custom.DateTimeField()
    owner = models.ForeignKey(CorporationSheet)

    def __unicode__(self):
        return "{0}'s assets ({1})".format(self.owner, self.retrieved)


class AssetManager(models.Manager):
    def search(self, corporationIDs, query):
        return self.raw('''
        SELECT
            *,
            ts_rank(search_tokens, plainto_tsquery(%(query)s)) as relevancy
        FROM
            corporation_asset
        WHERE
            owner_id IN %(corporationIDs)s AND
            search_tokens @@ plainto_tsquery(%(query)s)
        ORDER BY
            relevancy DESC;
        ''', {
            'query': query,
            'corporationIDs': tuple(corporationIDs)
        })

    def summarize(self, corporationIDs):
        with connections['default'].cursor() as cursor:
            cursor.execute('''
            SELECT COALESCE(
                ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(summary))),
                '[]'
            )
            FROM
              (SELECT
                 c.corporationName,
                 a.owner_id AS "corporationID",
                 sum(a.item_value)
               FROM
                 corporation_asset a,
                 corporation_corporationsheet c
               WHERE
                 a.owner_id IN %(corporationIDs)s AND
                 c."corporationID" = a.owner_id AND
                 c.enabled = TRUE
               GROUP BY c.corporationName, a.owner_id
               ORDER BY sum DESC) summary;
            ''', {'corporationIDs': tuple(corporationIDs)})

            return cursor.fetchone()[0]

    def net_worth(self, corporation):
        with connections['default'].cursor() as cursor:
            cursor.execute('''
            SELECT
               sum(a.item_value)
           FROM
             corporation_asset a
           WHERE
             a.owner_id = %(corporationID)s
            ''', {'corporationID': corporation.pk})

            return cursor.fetchone()[0]


class Asset(models.Model):
    itemID = models.BigIntegerField()
    quantity = models.BigIntegerField()
    locationID = models.BigIntegerField()
    locationName = models.CharField(max_length=255, blank=True, default='')
    regionID = models.IntegerField(null=True)
    solarSystemID = models.IntegerField(null=True)
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255)
    flag = models.IntegerField()
    singleton = models.BooleanField(default=False)
    rawQuantity = models.IntegerField(default=0)
    path = models.CharField(max_length=255, default='')
    parent_id = models.BigIntegerField(null=True)
    groupID = models.IntegerField(null=True)
    categoryID = models.IntegerField(null=True)
    search_tokens = models.TextField(null=True)

    item_value = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)
    item_volume = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)
    container_volume = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)
    container_value = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)

    owner = models.ForeignKey(CorporationSheet)

    objects = AssetManager()

    def update_search_tokens(self):
        with connections['default'].cursor() as cursor:
            if self.singleton:
                fitted = 'fitted'
            else:
                fitted = 'unfitted'
            try:
                item_type = self.get_type()
                group_name = item_type.group.groupName
                category_name = item_type.group.category.categoryName
            except InvType.DoesNotExist:
                group_name = ''
                category_name = ''

            cursor.execute('''
            UPDATE
                corporation_asset
            SET
                    search_tokens =
                        setweight(to_tsvector(unaccent(%(typeName)s)), 'B') ||
                        setweight(to_tsvector(unaccent(%(locationName)s)), 'B') ||
                        setweight(to_tsvector(unaccent(%(itemName)s)), 'A') ||
                        setweight(to_tsvector(unaccent(%(groupName)s)), 'D') ||
                        setweight(to_tsvector(unaccent(%(categoryName)s)), 'D') ||
                        setweight(to_tsvector(unaccent(%(fitted)s)), 'C') ||
                        setweight(to_tsvector(unaccent(%(owner)s)), 'B')
                WHERE
                    id = %(pk)s''',
                               {
                                   'pk': self.pk,
                                   'typeName': self.typeName,
                                   'locationName': self.locationName,
                                   'itemName': self.item_name(),
                                   'groupName': group_name,
                                   'categoryName': category_name,
                                   'fitted': fitted,
                                   'owner': self.owner.corporationName
                               })

    def item_name(self):
        try:
            return ItemLocationName.objects.get(itemID=self.itemID,
                                                owner=self.owner).itemName
        except ItemLocationName.DoesNotExist:
            return ''

    def from_item(self, item, path):
        self.itemID = item['itemID']
        self.quantity = item['quantity']
        self.locationID = item['locationID']
        self.locationName = item['locationName']
        self.typeID = item['typeID']
        self.typeName = item['typeName']
        self.flag = item['flag']
        self.singleton = item['singleton']
        self.path = ".".join(map(str, path))
        self.groupID = item['groupID']
        self.categoryID = item['categoryID']
        self.parent_id = item['parent_id']

        if 'rawQuantity' in item:
            self.rawQuantity = item['rawQuantity']

    def categorize(self):
        self.groupID = self.get_type().group.pk
        self.categoryID = self.get_type().group.category.pk

    def category(self):
        return self.get_type().group.category.pk

    def get_contents(self):
        return Asset.objects.filter(owner=self.owner,
                                    parent_id=self.itemID)

    def get_volume(self):
        if self.singleton:
            return self.item_volume + self.container_volume
        else:
            return self.item_volume

    def get_value(self):
        if self.singleton:
            return self.item_value + self.container_value
        else:
            return self.item_value

    def compute_statistics(self):
        if self.typeID == 51:
            # 51 is bookmark
            return
        from stationspinner.evecentral.pragma import get_item_market_value
        if self.rawQuantity > -2:
            self.item_value = get_item_market_value(self.typeID) * self.quantity
        try:
            item = InvType.objects.get(pk=self.typeID)
        except InvType.DoesNotExist:
            log.warning('TypeID {0} does not exist.'.format(self.typeID))
            return
        if not item.volume and item.volume != 0:
            log.warning('TypeID {0} has no volume.'.format(self.typeID))
            return
        if not self.singleton and item.group.pk in PACKAGED_VOLUME.keys():
            try:
                self.item_volume = get_item_packaged_volume(item.group.pk, item.pk) * self.quantity
            except UnknownPackagedItem:
                self.item_volume = 0.0
        else:
            self.item_volume = item.volume * self.quantity

    def compute_container_volume(self):
        volume = Decimal(0.0)
        contents = self.get_contents()
        for item in contents:
            volume += item.get_volume()
        self.container_volume = volume

    def compute_container_value(self):
        value = Decimal(0.0)
        contents = self.get_contents()
        for item in contents:
            value += item.get_value()
        self.container_value = value

    def update_from_api(self, item, handler):
        self.compute_statistics()
        try:
            location = get_location(self.locationID)
            self.regionID = get_location_regionID(location)
            self.solarSystemID = get_location_solarSystemID(location)
        except:
            pass

    def get_type(self):
        return InvType.objects.get(pk=self.typeID)

    def get_parent(self):
        if self.parent_id:
            return Asset.objects.get(itemID=self.parent_id)
        else:
            return None

    def parent_list(self):
        parent = self.get_parent()
        output = []
        if parent:
            output.append(
                {
                    'itemID': parent.itemID,
                    'typeName': parent.typeName,
                    'itemName': parent.item_name()
                }
            )
            if parent.get_parent():
                output.extend(parent.parent_list())
        return output

    def __unicode__(self):
        name = self.item_name()
        if name:
            return '{0} {1}'.format(self.typeName, name)
        else:
            return self.typeName

    class Meta(object):
        managed = False
        unique_together = ('itemID', 'owner')


class MarketOrder(models.Model):
    orderID = models.BigIntegerField()
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255, null=True)
    volEntered = models.BigIntegerField()
    minVolume = models.BigIntegerField()
    charID = models.BigIntegerField()
    accountKey = models.IntegerField(default=1000)
    issued = custom.DateTimeField()
    bid = models.BooleanField(default=False)
    range = models.IntegerField()
    escrow = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    stationID = models.BigIntegerField()
    orderState = models.IntegerField()
    volRemaining = models.BigIntegerField()
    duration = models.IntegerField()
    price = models.DecimalField(max_digits=30, decimal_places=2)

    owner = models.ForeignKey(CorporationSheet)

    def update_from_api(self, sheet, handler):
        try:
            self.typeName = InvType.objects.get(pk=self.typeID).typeName
        except InvType.DoesNotExist:
            log.warning('TypeID {0} does not exist.'.format(self.typeID))
            self.typeName = self.typeID

    class Meta(object):
        unique_together = ('owner', 'orderID')


class Contract(models.Model):
    status = models.CharField(max_length=50)
    startStationID = models.BigIntegerField(null=True)
    dateCompleted = custom.DateTimeField(null=True)
    collateral = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    assigneeID = models.BigIntegerField(null=True)
    issuerID = models.BigIntegerField()
    price = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    endStationID = models.BigIntegerField(null=True)
    buyout = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    dateExpired = custom.DateTimeField()
    availability = models.CharField(max_length=10)
    numDays = models.IntegerField(null=True)
    volume = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    title = models.CharField(max_length=255)
    acceptorID = models.BigIntegerField(null=True)
    forCorp = models.BooleanField(default=False)
    dateAccepted = custom.DateTimeField(null=True)
    dateIssued = custom.DateTimeField(null=True)
    reward = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    type = models.CharField(max_length=15)
    issuerCorpID = models.BigIntegerField()
    contractID = models.BigIntegerField()
    search_tokens = models.TextField(null=True)

    owner = models.ForeignKey(CorporationSheet)

    def get_items(self):
        return ContractItem.objects.filter(owner=self.owner,
                                           contract=self)

    def get_bids(self):
        return ContractBid.objects.fitler(owner=self.owner,
                                          contractID=self.contractID)

    class Meta(object):
        unique_together = ('owner', 'contractID')


class ContractItem(models.Model):
    contract = models.ForeignKey(Contract)
    recordID = models.BigIntegerField()
    typeID = models.IntegerField()
    quantity = models.BigIntegerField()
    rawQuantity = models.BigIntegerField(null=True)
    singleton = models.BooleanField(default=False)
    included = models.BooleanField(default=True)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('contract', 'owner', 'recordID')


class ContractBid(models.Model):
    bidID = models.BigIntegerField()
    contractID = models.BigIntegerField()
    bidderID = models.BigIntegerField()
    dateBid = custom.DateTimeField()
    amount = models.DecimalField(max_digits=30, decimal_places=2, null=True)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('bidID', 'contractID', 'owner')



class ContainerLog(models.Model):
    itemID = models.BigIntegerField()
    typeID = models.IntegerField(null=True)
    itemTypeID = models.IntegerField()
    actorName = models.CharField(max_length=255)
    flag = models.IntegerField()
    locationID = models.BigIntegerField()
    logTime = custom.DateTimeField()
    passwordType = models.CharField(max_length=9, default='', blank=True)
    action = models.CharField(max_length=50)
    actorID = models.BigIntegerField()
    quantity = models.BigIntegerField(null=True)


    owner = models.ForeignKey(CorporationSheet)

    def update_from_api(self, item, handler):
        if not item.typeID:
            self.typeID = None

    class Meta(object):
        unique_together = ('logTime', 'itemID', 'owner')


class NPCStanding(models.Model):
    STANDING_TYPE = (
        ('Agent', 'Agent'),
        ('Corporation', 'Corporation'),
        ('Faction', 'Faction')
    )
    type = models.CharField(max_length=11, choices=STANDING_TYPE)
    fromID = models.IntegerField()
    fromName = models.CharField(max_length=255)
    standing = models.DecimalField(max_digits=5, decimal_places=2)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('fromID', 'owner')


class MemberSecurity(models.Model):
    ROLE_LOCATION = (
        ('Global', 'Global'),
        ('Base', 'Base'),
        ('Other', 'Other'),
        ('HQ', 'HQ'),
    )
    roleID = models.BigIntegerField()
    roleName = models.CharField(max_length=100)
    location = models.CharField(max_length=10, choices=ROLE_LOCATION)
    characterID = models.IntegerField()
    characterName = models.CharField(max_length=255)
    grantable = models.BooleanField(default=False)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'characterID', 'roleID', 'location')


class MemberTitle(models.Model):
    characterID = models.IntegerField()
    characterName = models.CharField(max_length=255)
    titleID = models.IntegerField()
    titleName = models.CharField(max_length=255)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('owner', 'characterID', 'titleID')


class MemberSecurityLog(models.Model):
    changeTime = custom.DateTimeField()
    issuerID = models.IntegerField()
    issuerName = models.CharField(max_length=255)
    characterID = models.IntegerField()
    characterName = models.CharField(max_length=255)
    roleLocationType = models.CharField(max_length=255)
    oldRoles = JSONField(default=[])
    newRoles = JSONField(default=[])

    owner = models.ForeignKey(CorporationSheet)

    def update_from_api(self, item, *args, **kwargs):
        old_roles = []
        new_roles = []
        for role in item.oldRoles:
            old_roles.append({'roleID': role.roleID, 'roleName': role.roleName})
        for role in item.newRoles:
            new_roles.append({'roleID': role.roleID, 'roleName': role.roleName})
        self.oldRoles = old_roles
        self.newRoles = new_roles

    class Meta(object):
        unique_together = ('owner', 'changeTime', 'characterID', 'roleLocationType')


class Facility(models.Model):
    facilityID = models.BigIntegerField()
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255)
    solarSystemID = models.IntegerField()
    solarSystemName = models.CharField(max_length=255)
    regionID = models.IntegerField()
    regionName = models.CharField(max_length=255)
    tax = models.DecimalField(max_digits=6, decimal_places=3)
    starbaseModifier = models.IntegerField(default=0)

    owner = models.ForeignKey(CorporationSheet)

    class Meta(object):
        unique_together = ('facilityID', 'owner')


class Division(models.Model):
    accountKey = models.IntegerField()
    description = models.CharField(max_length=255)

    owner = models.ForeignKey(CorporationSheet)

    def __unicode__(self):
        return self.description

    class Meta(object):
        unique_together = ('accountKey', 'owner')


class WalletDivision(models.Model):
    accountKey = models.IntegerField()
    description = models.CharField(max_length=255)

    owner = models.ForeignKey(CorporationSheet)

    def __unicode__(self):
        return self.description

    class Meta(object):
        unique_together = ('accountKey', 'owner')



class AccountBalance(models.Model):
    accountKey = models.IntegerField()
    balance = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    accountID = models.IntegerField(null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    owner = models.ForeignKey(CorporationSheet)

    def get_division(self):
        try:
            return WalletDivision.objects.get(accountKey=self.accountKey,
                                              owner=self.owner)
        except WalletDivision.DoesNotExist:
            return self.accountKey

    class Meta(object):
        unique_together = ('accountID', 'owner')


class ItemLocationName(models.Model):
    itemID = models.BigIntegerField(primary_key=True)
    itemName = models.CharField(max_length=255)
    owner = models.ForeignKey(CorporationSheet)
    x = models.BigIntegerField(default=0)
    y = models.BigIntegerField(default=0)
    z = models.BigIntegerField(default=0)

    def __unicode__(self):
        return self.itemName

    class Meta(object):
        unique_together = ('itemID', 'owner')


class CustomsOffice(models.Model):
    itemID = models.BigIntegerField()
    solarSystemID = models.IntegerField()
    solarSystemName = models.CharField(max_length=255)
    reinforceHour = models.IntegerField()
    allowAlliance = models.BooleanField()
    allowStandings = models.BooleanField()
    standingLevel = models.IntegerField()
    taxRateAlliance = models.DecimalField(max_digits=6, decimal_places=3)
    taxRateCorporation = models.DecimalField(max_digits=6, decimal_places=3)
    taxRateStandingHigh = models.DecimalField(max_digits=6, decimal_places=3)
    taxRateStandingGood = models.DecimalField(max_digits=6, decimal_places=3)
    taxRateStandingNeutral = models.DecimalField(max_digits=6, decimal_places=3)
    taxRateStandingBad = models.DecimalField(max_digits=6, decimal_places=3)
    taxRateStandingHorrible = models.DecimalField(max_digits=6, decimal_places=3)

    owner = models.ForeignKey(CorporationSheet)

    def save(self, *args, **kwargs):
        for tax_target in ('taxRateAlliance',
                           'taxRateCorporation',
                           'taxRateStandingHigh',
                           'taxRateStandingGood',
                           'taxRateStandingNeutral',
                           'taxRateStandingBad',
                           'taxRateStandingHorrible'):
            if getattr(self, tax_target) is None:
                setattr(self, tax_target, 0.0)
        return super(CustomsOffice, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.solarSystemName

    class Meta(object):
        unique_together = ('itemID', 'solarSystemID')


@receiver(post_save, sender=CorporationSheet)
def update_apidata(sender, instance=None, created=False, **kwargs):
    if created:
        app.send_task('accounting.update_corporation_apidata', (instance.pk,))