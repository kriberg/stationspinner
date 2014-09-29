from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from stationspinner.accounting.models import APIKey, APIUpdate, Capsuler
from stationspinner.libs import fields as custom


class CharacterSheet(models.Model):
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    owner_key = models.ForeignKey(APIKey, null=True)
    owner = models.ForeignKey(Capsuler)
    enabled = models.BooleanField(default=False)

    # Autoparsed:
    # DoB
    # allianceID
    # allianceName
    # ancestry
    # balance
    # bloodLine
    # characterID
    # cloneName
    # cloneSkillPoints
    # corporationID
    # corporationName
    # factionID
    # factionName
    # gender
    # name
    # race

    characterID = models.IntegerField(primary_key=True)                                     # auto
    name = models.CharField(max_length=255)                                                 # auto
    cloneSkillPoints = models.IntegerField()                                                # auto
    corporationID = models.IntegerField()                                                   # auto
    corporationName = models.CharField(max_length=255)                                      # auto
    bloodLine = models.CharField(max_length=50)                                             # auto
    factionID = models.IntegerField(null=True, default=None)                                # auto
    factionName = models.CharField(max_length=100, null=True, default=None)                 # auto
    allianceName = models.CharField(max_length=255, blank=True, null=True, default=None)    # auto
    ancestry = models.CharField(max_length=100)                                             # auto
    balance = models.DecimalField(max_digits=30, decimal_places=2, null=True)               # auto
    DoB = custom.DateTimeField()                                                            # auto
    gender = models.CharField(max_length=6, choices=GENDER)                                 # auto
    race = models.CharField(max_length=20)                                                  # auto
    allianceID = models.IntegerField(null=True)                                             # auto
    cloneName = models.CharField(max_length=255, blank=True, null=True)                     # auto

    # Base attributes
    charisma = models.IntegerField()
    perception = models.IntegerField()
    intelligence = models.IntegerField()
    memory = models.IntegerField()
    willpower = models.IntegerField()
    # Enhancers
    charismaAugmentatorValue = models.IntegerField(default=0)
    perceptionAugmentatorValue = models.IntegerField(default=0)
    intelligenceAugmentatorValue = models.IntegerField(default=0)
    memoryAugmentatorValue = models.IntegerField(default=0)
    willpowerAugmentatorValue = models.IntegerField(default=0)
    charismaAugmentatorName = models.CharField(default=None, null=True, max_length=255)
    perceptionAugmentatorName = models.CharField(default=None, null=True, max_length=255)
    intelligenceAugmentatorName = models.CharField(default=None, null=True, max_length=255)
    memoryAugmentatorName = models.CharField(default=None, null=True, max_length=255)
    willpowerAugmentatorName = models.CharField(default=None, null=True, max_length=255)

    def __unicode__(self):
        return self.name

    def update_from_api(self, sheet, handler):
        handler.autoparse(sheet, self)
        handler.autoparse(sheet.attributes, self)

        if not sheet.attributeEnhancers == '':
            boosted = filter(lambda x: str(x).endswith('Bonus'), dir(sheet.attributeEnhancers))
            for attribute in boosted:
                augmentator = getattr(sheet.attributeEnhancers, attribute)
                # This just clips away the Bonus part of the name
                base_name = attribute[:-5]
                setattr(self, '{0}AugmentatorValue'.format(base_name), augmentator.augmentatorValue)
                setattr(self, '{0}AugmentatorName'.format(base_name), augmentator.augmentatorName)
        self.enabled = True
        self.save()

        handler.autoparseList(sheet.skills,
                              Skill,
                              unique_together=('typeID',),
                              extra_selectors={'owner': self},
                              owner=self,
                              pre_save=True)

        handler.autoparseList(sheet.corporationRoles,
                              CorporationRole,
                              unique_together=('roleID', 'roleName'),
                              extra_selectors={'owner': self, 'location': 'Global'},
                              pre_save=True)

        handler.autoparseList(sheet.corporationRolesAtBase,
                              CorporationRole,
                              unique_together=('roleID', 'roleName'),
                              extra_selectors={'owner': self, 'location': 'Base'},
                              pre_save=True)

        handler.autoparseList(sheet.corporationRolesAtOther,
                              CorporationRole,
                              unique_together=('roleID', 'roleName'),
                              extra_selectors={'owner': self, 'location': 'Other'},
                              pre_save=True)

        handler.autoparseList(sheet.corporationRolesAtHQ,
                              CorporationRole,
                              unique_together=('roleID', 'roleName'),
                              extra_selectors={'owner': self, 'location': 'HQ'},
                              pre_save=True)

        handler.autoparseList(sheet.corporationTitles,
                              CorporationTitle,
                              unique_together=('titleID', 'titleName'),
                              extra_selectors={'owner': self},
                              pre_save=True)

        handler.autoparseList(sheet.certificates,
                              Certificate,
                              unique_together=('titleID', 'titleName'),
                              extra_selectors={'owner': self},
                              pre_save=True)


class UpcomingCalendarEvent(models.Model):
    eventID = models.IntegerField()
    eventTitle = models.CharField(max_length=255, blank=True, null=True)
    importance = models.BooleanField(default=False)
    response = models.CharField(max_length=20)
    ownerName = models.CharField(max_length=255, blank=True)
    duration = models.IntegerField()
    ownerID = models.IntegerField()
    eventDate = custom.DateTimeField()
    eventText = models.TextField(blank=True, default='')
    ownerTypeID = models.IntegerField()
    owner = models.ForeignKey(CharacterSheet)


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

    owner = models.ForeignKey(CharacterSheet)

    class Meta:
        unique_together = ('itemID', 'owner')


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

    owner = models.ForeignKey(CharacterSheet)


class Research(models.Model):
    pointsPerDay = models.DecimalField(max_digits=10, decimal_places=2)
    researchStartDate = custom.DateTimeField()
    skillTypeID = models.IntegerField()
    agentID = models.IntegerField()
    remainderPoints = models.DecimalField(max_digits=20, decimal_places=10)

    owner = models.ForeignKey(CharacterSheet)


class Asset(MPTTModel):
    itemID = models.BigIntegerField()
    typeID = models.IntegerField(null=True)
    singleton = models.BooleanField(default=False)
    locationID = models.BigIntegerField()
    flag = models.IntegerField()
    quantity = models.IntegerField()
    parent = TreeForeignKey('self', null=True, blank=True, related_name="children")

    owner = models.ForeignKey(CharacterSheet)


class MarketOrder(models.Model):
    orderID = models.IntegerField()
    typeID = models.IntegerField()
    volEntered = models.IntegerField()
    minVolume = models.IntegerField()
    charID = models.IntegerField()
    accountKey = models.IntegerField(default=1000)
    issued = custom.DateTimeField()
    bid = models.BooleanField(default=False)
    range = models.IntegerField()
    escrow = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    stationID = models.IntegerField()
    orderState = models.IntegerField()
    volRemaining = models.IntegerField()
    duration = models.IntegerField()
    price = models.DecimalField(max_digits=30, decimal_places=2)

    owner = models.ForeignKey(CharacterSheet)


class Medal(models.Model):
    medalID = models.BigIntegerField()
    status = models.CharField(max_length=10)
    issued = custom.DateTimeField()
    issuerID = models.IntegerField()
    reason = models.TextField(blank=True, default='')
    title = models.CharField(max_length=255, null=True)
    corporationID = models.IntegerField(null=True)
    description = models.TextField(blank=True, default='')

    owner = models.ForeignKey(CharacterSheet)


class PlanetaryColony(models.Model):
    lastUpdate = custom.DateTimeField()
    solarSystemName = models.CharField(max_length=100)
    planetName = models.CharField(max_length=255)
    upgradeLevel = models.IntegerField()
    numberOfPins = models.IntegerField()
    planetID = models.IntegerField()
    ownerName = models.CharField(max_length=255)
    ownerID = models.IntegerField()
    planetRypeID = models.IntegerField()
    solarSystemID = models.IntegerField()
    planetTypeName = models.CharField(max_length=50)

    owner = models.ForeignKey(CharacterSheet)

    class Meta:
        verbose_name_plural = "PlanetaryColonies"


class WalletJournal(models.Model):
    taxReceiverID = models.IntegerField(null=True)
    argName1 = models.CharField(max_length=255, blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    date = custom.DateTimeField()
    refTypeID = models.IntegerField(null=True)
    refID = models.IntegerField(null=True)
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

    owner = models.ForeignKey(CharacterSheet)


class Notification(models.Model):
    typeID = models.IntegerField()
    notificationID = models.IntegerField()
    sentDate = custom.DateTimeField()
    read = models.BooleanField(default=False)
    senderName = models.CharField(max_length=255)
    senderID = models.IntegerField()

    owner = models.ForeignKey(CharacterSheet)


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

    owner = models.ForeignKey(CharacterSheet)

    def get_items(self):
        return ContractItem.objects.filter(contract=self, owner=self.owner)

    def get_included_items(self):
        return self.get_items().filter(included=True)

    def get_wanted_items(self):
        return self.get_items().filter(included=False)


class ContractItem(models.Model):
    contract = models.ForeignKey(Contract)
    rowID = models.BigIntegerField()
    typeID = models.IntegerField()
    quantity = models.BigIntegerField()
    rawQuantity = models.IntegerField(null=True)
    singleton = models.BooleanField(default=False)
    included = models.BooleanField(default=True)

    owner = models.ForeignKey(CharacterSheet)

    class Meta:
        unique_together = ('contract', 'owner', 'rowID')


class ContractBid(models.Model):
    bidID = models.BigIntegerField()
    contractID = models.BigIntegerField()
    bidderID = models.BigIntegerField()
    dateBid = custom.DateTimeField()
    amount = models.DecimalField(max_digits=30, decimal_places=2, null=True)

    owner = models.ForeignKey(CharacterSheet)

    class Meta:
        unique_together = ('bidID', 'contractID', 'owner')


class SkillQueue(models.Model):
    typeID = models.IntegerField()
    endTime = custom.DateTimeField()
    startTime = custom.DateTimeField()
    level = models.IntegerField()
    queuePosition = models.IntegerField()
    startSP = models.IntegerField()
    endSP = models.IntegerField()

    owner = models.ForeignKey(CharacterSheet)


class MailingList(models.Model):
    listID = models.IntegerField()
    displayName = models.CharField(max_length=255)

    owner = models.ForeignKey(CharacterSheet)



class ContactNotification(models.Model):
    notificationID = models.BigIntegerField()
    senderID = models.IntegerField()
    senderName = models.CharField(max_length=255)
    messageData = models.TextField(blank='', default='')
    sentDate = custom.DateTimeField()

    owner = models.ForeignKey(CharacterSheet)


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

    owner = models.ForeignKey(CharacterSheet)


class CorporationRole(models.Model):
    ROLE_LOCATION = (
        ('Global', 'Global'),
        ('Base', 'Base'),
        ('Other', 'Other'),
        ('HQ', 'HQ'),
    )
    roleID = models.BigIntegerField()
    roleName = models.CharField(max_length=100)
    location = models.CharField(max_length=10, choices=ROLE_LOCATION)

    owner = models.ForeignKey(CharacterSheet)


class CorporationTitle(models.Model):
    titleID = models.IntegerField()
    titleName = models.CharField(max_length=255)

    owner = models.ForeignKey(CharacterSheet)


class Skill(models.Model):
    skillpoints = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    typeID = models.IntegerField()
    published = models.BooleanField(default=True)

    owner = models.ForeignKey(CharacterSheet)

    class Meta:
        unique_together = ('typeID', 'owner')


class Certificate(models.Model):
    certificateID = models.IntegerField()

    owner = models.ForeignKey(CharacterSheet)

    class Meta:
        unique_together = ('certificateID', 'owner')


class MailMessage(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    senderName = models.CharField(max_length=255, blank=True, null=True)
    senderID = models.IntegerField()
    toCorpOrAllianceID = models.IntegerField(null=True)
    sentDate = custom.DateTimeField()
    messageID = models.BigIntegerField()
    toListID = models.TextField(blank=True, default='')
    toCharacterIDs = models.TextField(blank=True, default='')

    owner = models.ForeignKey(CharacterSheet)

    class Meta:
        unique_together = ('messageID', 'owner')


class SkillInTraining(models.Model):
    trainingStartSP = models.IntegerField(null=True)
    trainingTypeID = models.IntegerField(null=True)
    trainingDestinationSP = models.IntegerField(null=True)
    currentTQTime = custom.DateTimeField()
    trainingEndTime = custom.DateTimeField(null=True)
    skillInTraining = models.BooleanField(default=True)
    trainingStartTime = custom.DateTimeField(null=True)
    trainingToLevel = models.IntegerField(null=True)

    owner = models.ForeignKey(CharacterSheet)


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

    owner = models.ForeignKey(CharacterSheet)

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

    owner = models.ForeignKey(CharacterSheet)


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

    owner = models.ForeignKey(CharacterSheet)

    class Meta:
        unique_together = ('fromID', 'owner')