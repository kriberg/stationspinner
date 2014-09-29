from django.db import models
from django_hstore import hstore
from stationspinner.accounting.models import APIKey, APIUpdate
from stationspinner.libs import fields as custom
from stationspinner.character import models as character_models


class CorporationSheet(models.Model):
    owner_key = models.ForeignKey(APIKey)
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
    general_settings = hstore.DictionaryField(default={})

    # Combat settings
    combat_settings = hstore.DictionaryField(default={})

    owner = models.ForeignKey(CorporationSheet)
    objects = hstore.HStoreManager()


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


class Blueprint(character_models.Blueprint):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class IndustryJob(character_models.IndustryJob):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class IndustryJobHistory(character_models.IndustryJobHistory):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class WalletTransaction(character_models.WalletTransaction):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class WalletJournal(character_models.WalletJournal):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class Contact(character_models.Contact):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class Asset(character_models.Asset):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class MarketOrder(character_models.MarketOrder):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class Contract(character_models.Contract):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class ContractItem(character_models.ContractItem):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class ContractBid(character_models.ContractBid):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')



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


class NPCStanding(character_models.NPCStanding):
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class MemberSecurity(character_models.CorporationRole):
    characterID = models.IntegerField()
    characterName = models.CharField(max_length=255)
    grantable = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


class MemberTitle(character_models.CorporationTitle):
    characterID = models.IntegerField()
    characterName = models.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        owner = models.ForeignKey(CorporationSheet)
        owner.contribute_to_class(models.ForeignKey, 'owner')


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


class WalletDivision(Division):
    pass


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


