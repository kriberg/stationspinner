from django.db import models
from django_pgjson.fields import JsonField, JsonBField
from stationspinner.accounting.models import APIKey, Capsuler
from stationspinner.libs import fields as custom
from stationspinner.character import models as character_models


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

    def update_from_api(self, sheet, handler):
        handler.autoparse(sheet, self)
        self.enabled = True
        self.save()

        handler.autoparseList(sheet.divisions,
                              Division,
                              unique_together=('accountKey',),
                              extra_selectors={'owner': self},
                              owner=self,
                              pre_save=True)

        handler.autoparseList(sheet.walletDivisions,
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


    shareholderID = models.IntegerField()
    shareholderName = models.CharField(max_length=255)
    shareholderCorporationID = models.IntegerField(null=True)
    shareholderCorporationName = models.CharField(max_length=255, null=True)
    shares = models.IntegerField(default=1)

    owner = models.ForeignKey(CorporationSheet)


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


class MemberMedal(models.Model):
    medalID = models.BigIntegerField()
    status = models.CharField(max_length=10)
    issued = custom.DateTimeField()
    issuerID = models.IntegerField()
    reason = models.TextField(blank=True, default='')
    title = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, default='')

    owner = models.ForeignKey(CorporationSheet)

    class Meta:
        unique_together = ('medalID', 'owner')


class Medal(models.Model):
    medalID = models.BigIntegerField()
    title = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, default='')
    created = custom.DateTimeField()
    creatorID = models.IntegerField()

    owner = models.ForeignKey(CorporationSheet)

    class Meta:
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
    general_settings = JsonField(default={}, blank=True)

    # Combat settings
    combat_settings = JsonField(default={}, blank=True)

    owner = models.ForeignKey(CorporationSheet)


    def get_state(self):
        return self.STATES[self.state]

    def get_fuel(self):
        return StarbaseFuel.objects.filter(starbase=self)

    class Meta:
        unique_together = ('itemID', 'owner')


class StarbaseFuel(models.Model):
    starbase = models.ForeignKey(Starbase)
    typeID = models.IntegerField()
    quantity = models.IntegerField()

    owner = models.ForeignKey(CorporationSheet)


class Outpost(models.Model):
    stationID = models.IntegerField(primary_key=True)
    stationName = models.CharField(max_length=255)
    reprocessingEfficiency = models.DecimalField(max_digits=30, decimal_places=10, default=0.0)
    reprocessingStationTake = models.DecimalField(max_digits=30, decimal_places=10, default=0.0)
    officeRentalCost = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    dockingCostPerShipColume = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)
    standingOwnerID = models.IntegerField()
    ownerID = models.IntegerField()
    solarSystemID = models.IntegerField()
    stationTypeID = models.IntegerField()

    owner = models.ForeignKey(CorporationSheet)

    class Meta:
        unique_together = ('stationID', 'owner')


class OutpostService(models.Model):
    outpost = models.ForeignKey(Outpost)
    serviceName = models.CharField(max_length=255)
    minStanding = models.DecimalField(max_digits=5, decimal_places=2)
    surchargePerBadStanding = models.IntegerField()
    discountPerGoodStanding = models.IntegerField()

    owner = models.ForeignKey(CorporationSheet)

    class Meta:
        unique_together = ('outpost', 'serviceName', 'owner')


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

    class Meta:
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
    completedCharacterID = models.IntegerField(null=True)
    installerName = models.CharField(max_length=255)
    installerID = models.IntegerField()
    facilityID = models.IntegerField()
    pauseDate = custom.DateTimeField(null=True)
    solarSystemName = models.CharField(max_length=255)
    stationID = models.IntegerField(null=True)
    jobID = models.BigIntegerField(null=True)
    teamID = models.IntegerField(null=True)
    productTypeName = models.CharField(max_length=255, blank=True, null=True)
    blueprintLocationID = models.IntegerField(null=True)
    blueprintID = models.BigIntegerField(null=True)
    solarSystemID = models.IntegerField()
    licensedRuns = models.IntegerField(null=True)

    owner = models.ForeignKey(CorporationSheet)


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
    blueprintTypeID = models.IntegerField(null=True)
    timeInSeconds = models.IntegerField()
    productTypeID = models.IntegerField(null=True)
    completedDate = custom.DateTimeField(null=True)
    completedCharacterID = models.IntegerField(null=True)
    installerName = models.CharField(max_length=255)
    installerID = models.IntegerField()
    facilityID = models.IntegerField()
    pauseDate = custom.DateTimeField(null=True)
    solarSystemName = models.CharField(max_length=255)
    stationID = models.IntegerField(null=True)
    jobID = models.BigIntegerField(null=True)
    teamID = models.IntegerField(null=True)
    productTypeName = models.CharField(max_length=255, blank=True, null=True)
    blueprintLocationID = models.IntegerField(null=True)
    blueprintID = models.BigIntegerField(null=True)
    solarSystemID = models.IntegerField()
    licensedRuns = models.IntegerField(null=True)

    owner = models.ForeignKey(CorporationSheet)


class WalletTransaction(models.Model):
    typeID = models.IntegerField(null=True)
    clientTypeID = models.IntegerField(null=True)
    transactionFor = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    clientID = models.IntegerField(null=True)
    journalTransactionID = models.IntegerField(null=True)
    typeName = models.CharField(max_length=255, blank=True, null=True)
    stationID = models.IntegerField(null=True)
    stationName = models.CharField(max_length=255, blank=True, null=True)
    transactionID = models.IntegerField(null=True)
    quantity = models.IntegerField(null=True)
    transactionDateTime = custom.DateTimeField(null=True)
    clientName = models.CharField(max_length=255, blank=True, null=True)
    transactionType = models.CharField(max_length=255, blank=True, null=True)

    owner = models.ForeignKey(CorporationSheet)

class WalletJournal(models.Model):
    taxReceiverID = models.CharField(max_length=255, blank=True, null=True)
    argName1 = models.CharField(max_length=255, blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    date = custom.DateTimeField()
    refTypeID = models.IntegerField(null=True)
    refID = models.BigIntegerField(null=True)
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

    owner = models.ForeignKey(CorporationSheet)


class Contact(models.Model):
    CONTACT_LIST_TYPES = (
        ('Private', 'Private'),
        ('Corporate', 'Corporate'),
        ('Alliance', 'Alliance')
    )
    standing = models.IntegerField()
    inWatchlist = models.BooleanField(default=False)
    contactID = models.IntegerField()
    contactName = models.CharField(max_length=255)
    contactTypeID = models.IntegerField()
    listType = models.CharField(max_length=20, choices=CONTACT_LIST_TYPES)

    owner = models.ForeignKey(CorporationSheet)


class AssetList(models.Model):
    items = JsonBField()
    retrieved = custom.DateTimeField()
    owner = models.ForeignKey(CorporationSheet)

    def __unicode__(self):
        return "{0}'s assets ({1})".format(self.owner, self.retrieved)


class Asset(models.Model):
    itemID = models.BigIntegerField()
    quantity = models.BigIntegerField()
    locationID = models.BigIntegerField()
    typeID = models.IntegerField()
    flag = models.IntegerField()
    singleton = models.BooleanField(default=False)
    rawQuantity = models.IntegerField(default=0)
    path = models.CharField(max_length=255, default='')

    owner = models.ForeignKey(CorporationSheet)

    def from_item(self, item):
        self.itemID = item['itemID']
        self.quantity = item['quantity']
        self.locationID = item['locationID']
        self.typeID = item['typeID']
        self.flag = item['flag']
        self.singleton = item['singleton']
        self.path = ".".join(map(str, item['path']))

        if 'rawQuantity' in item:
            self.rawQuantity = item['rawQuantity']


    class Meta:
        managed = False


class MarketOrder(models.Model):
    orderID = models.BigIntegerField()
    typeID = models.IntegerField()
    volEntered = models.BigIntegerField()
    minVolume = models.BigIntegerField()
    charID = models.IntegerField()
    accountKey = models.IntegerField(default=1000)
    issued = custom.DateTimeField()
    bid = models.BooleanField(default=False)
    range = models.IntegerField()
    escrow = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    stationID = models.IntegerField()
    orderState = models.IntegerField()
    volRemaining = models.BigIntegerField()
    duration = models.IntegerField()
    price = models.DecimalField(max_digits=30, decimal_places=2)

    owner = models.ForeignKey(CorporationSheet)


class Contract(models.Model):
    status = models.CharField(max_length=50)
    startStationID = models.IntegerField(null=True)
    dateCompleted = custom.DateTimeField(null=True)
    collateral = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    assigneeID = models.IntegerField(null=True)
    issuerID = models.IntegerField()
    price = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    endStationID = models.IntegerField(null=True)
    buyout = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    dateExpired = custom.DateTimeField()
    availability = models.CharField(max_length=10)
    numDays = models.IntegerField(null=True)
    volume = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    title = models.CharField(max_length=255)
    acceptorID = models.IntegerField(null=True)
    forCorp = models.BooleanField(default=False)
    dateAccepted = custom.DateTimeField(null=True)
    dateIssued = custom.DateTimeField(null=True)
    reward = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    type = models.CharField(max_length=15)
    issuerCorpID = models.IntegerField()
    contractID = models.BigIntegerField()

    owner = models.ForeignKey(CorporationSheet)


class ContractItem(models.Model):
    contract = models.ForeignKey(Contract)
    rowID = models.BigIntegerField()
    typeID = models.IntegerField()
    quantity = models.BigIntegerField()
    rawQuantity = models.IntegerField(null=True)
    singleton = models.BooleanField(default=False)
    included = models.BooleanField(default=True)

    owner = models.ForeignKey(CorporationSheet)

    class Meta:
        unique_together = ('contract', 'owner', 'rowID')


class ContractBid(models.Model):
    bidID = models.BigIntegerField()
    contractID = models.BigIntegerField()
    bidderID = models.BigIntegerField()
    dateBid = custom.DateTimeField()
    amount = models.DecimalField(max_digits=30, decimal_places=2, null=True)

    owner = models.ForeignKey(CorporationSheet)

    class Meta:
        unique_together = ('bidID', 'contractID', 'owner')



class ContainerLog(models.Model):
    itemID = models.BigIntegerField()
    typeID = models.IntegerField(null=True)
    itemTypeID = models.IntegerField()
    actorName = models.CharField(max_length=255)
    flag = models.IntegerField()
    locationID = models.IntegerField()
    logTime = custom.DateTimeField()
    passwordType = models.CharField(max_length=9, default='', blank=True)
    action = models.CharField(max_length=50)
    actorID = models.IntegerField()
    quantity = models.IntegerField(null=True)

    owner = models.ForeignKey(CorporationSheet)


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

    class Meta:
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


class MemberTitle(models.Model):
    characterID = models.IntegerField()
    characterName = models.CharField(max_length=255)
    titleID = models.IntegerField()
    titleName = models.CharField(max_length=255)

    owner = models.ForeignKey(CorporationSheet)


class MemberSecurityLog(models.Model):
    CHANGE_TYPES = (
        ('New', 'New'),
        ('Old', 'Old')
    )
    changeTime = custom.DateTimeField()
    issuerID = models.IntegerField()
    issuerName = models.CharField(max_length=255)
    characterID = models.IntegerField()
    characterName = models.CharField(max_length=255)
    roleLocationType = models.CharField(max_length=255)
    change_type = models.CharField(max_length=3, choices=CHANGE_TYPES)
    roleID = models.BigIntegerField()
    roleName = models.CharField(max_length=255)

    owner = models.ForeignKey(CorporationSheet)


class Facilities(models.Model):
    facilityID = models.BigIntegerField()
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255)
    solarSystemID = models.IntegerField()
    solarSystemName = models.CharField(max_length=255)
    regionID = models.IntegerField()
    regionName = models.CharField(max_length=255)
    tax = models.IntegerField(default=0)
    starbaseModifier = models.IntegerField(default=0)

    owner = models.ForeignKey(CorporationSheet)

    class Meta:
        unique_together = ('facilityID', 'owner')


class Division(models.Model):
    accountKey = models.IntegerField()
    description = models.CharField(max_length=255)

    owner = models.ForeignKey(CorporationSheet)

    def __unicode__(self):
        return self.description

    class Meta:
        unique_together = ('accountKey', 'owner')


class WalletDivision(models.Model):
    accountKey = models.IntegerField()
    description = models.CharField(max_length=255)

    owner = models.ForeignKey(CorporationSheet)

    def __unicode__(self):
        return self.description

    class Meta:
        unique_together = ('accountKey', 'owner')



class AccountBalance(models.Model):
    accountKey = models.IntegerField()
    balance = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    accountID = models.IntegerField(null=True)

    owner = models.ForeignKey(CorporationSheet)

    def get_division(self):
        return WalletDivision.objects.get(accountKey=self.accountKey,
                                          owner=self.owner)

    class Meta:
        unique_together = ('accountID', 'owner')


