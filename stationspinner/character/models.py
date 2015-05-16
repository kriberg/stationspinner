from django.db import models
from django.db.models import Sum
from stationspinner.accounting.models import APIKey, Capsuler
from stationspinner.universe.models import EveName
from stationspinner.libs import fields as custom, api_parser
from stationspinner.libs.api_parser import parse_evemail
from django_pgjson.fields import JsonBField
from stationspinner.sde.models import InvType, InvGroup
from django.db.models.signals import post_save
from django.dispatch import receiver
from stationspinner.celery import app
from stationspinner.settings import PRICE_INDEX_SYSTEM
from stationspinner.libs.pragma import get_location_id, get_item_packaged_volume, PACKAGED_VOLUME
from stationspinner.evecentral.models import MarketItem

class Skill(models.Model):
    skillpoints = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255, null=True)
    published = models.BooleanField(default=True)
    skill_group = models.CharField(max_length=50, null=True)

    owner = models.ForeignKey('CharacterSheet', related_name='skills')

    def update_from_api(self, data, handler):
        skill = InvType.objects.get(pk=self.typeID)
        self.typeName = skill.typeName
        self.skill_group = InvGroup.objects.get(pk=skill.groupID).groupName
        self.save()

    class Meta:
        unique_together = ('typeID', 'owner')




class CharacterSheet(models.Model):
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    owner_key = models.ForeignKey(APIKey, null=True)
    owner = models.ForeignKey(Capsuler)
    enabled = models.BooleanField(default=False)

    # From the api
    characterID = models.IntegerField(primary_key=True)                                     # auto
    name = models.CharField(max_length=255)                                                 # auto
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
    cloneJumpDate = custom.DateTimeField(null=True)
    freeRespecs = models.IntegerField(default=0)
    lastRespecDate = custom.DateTimeField(null=True)
    lastTimedRespec = custom.DateTimeField(null=True)
    freeSkillPoints = models.IntegerField(default=0)
    homeStationID = models.IntegerField(default=0)
    jumpActivation = custom.DateTimeField(null=True)
    jumpFatigue = custom.DateTimeField(null=True)
    jumpLastUpdate = custom.DateTimeField(null=True)
    remoteStationDate = custom.DateTimeField(null=True)

    # Computed
    skillPoints = models.IntegerField(default=0)

    # Base attributes
    charisma = models.IntegerField()
    perception = models.IntegerField()
    intelligence = models.IntegerField()
    memory = models.IntegerField()
    willpower = models.IntegerField()

    def __unicode__(self):
        return self.name

    def update_from_api(self, sheet, handler):
        handler.autoparse(sheet, self, ignore=('skills',))
        handler.autoparse(sheet.attributes, self)
        EveName.objects.register(self.pk, self.name)

        self.enabled = True
        self.save()


        implants = handler.autoparse_list(sheet.implants,
                              CharacterImplant,
                              unique_together=('typeID',),
                              extra_selectors={'owner': self},
                              owner=self,
                              pre_save=True)
        CharacterImplant.objects.filter(owner=self).exclude(pk__in=implants).delete()

        handler.autoparse_list(sheet.skills,
                              Skill,
                              unique_together=('typeID',),
                              extra_selectors={'owner': self},
                              owner=self,
                              pre_save=True)

        self.recalculate_skillpoints()

        clones = handler.autoparse_list(sheet.jumpClones,
                              JumpClone,
                              unique_together=('jumpCloneID',),
                              extra_selectors={'owner': self},
                              owner=self,
                              pre_save=True)
        JumpClone.objects.filter(owner=self).exclude(pk__in=clones).delete()

        clone_implants = handler.autoparse_list(sheet.jumpCloneImplants,
                              JumpCloneImplant,
                              unique_together=('jumpCloneID',),
                              extra_selectors={'owner': self},
                              owner=self,
                              pre_save=True)
        JumpCloneImplant.objects.filter(owner=self).exclude(pk__in=clone_implants).delete()


        roles = handler.autoparse_list(sheet.corporationRoles,
                              CorporationRole,
                              unique_together=('roleID', 'roleName'),
                              extra_selectors={'owner': self, 'location': 'Global'},
                              pre_save=True)

        roles += handler.autoparse_list(sheet.corporationRolesAtBase,
                              CorporationRole,
                              unique_together=('roleID', 'roleName'),
                              extra_selectors={'owner': self, 'location': 'Base'},
                              pre_save=True)

        roles += handler.autoparse_list(sheet.corporationRolesAtOther,
                              CorporationRole,
                              unique_together=('roleID', 'roleName'),
                              extra_selectors={'owner': self, 'location': 'Other'},
                              pre_save=True)

        roles += handler.autoparse_list(sheet.corporationRolesAtHQ,
                              CorporationRole,
                              unique_together=('roleID', 'roleName'),
                              extra_selectors={'owner': self, 'location': 'HQ'},
                              pre_save=True)

        CorporationRole.objects.filter(owner=self).exclude(pk__in=roles).delete()


        titles = handler.autoparse_list(sheet.corporationTitles,
                              CorporationTitle,
                              unique_together=('titleID', 'titleName'),
                              extra_selectors={'owner': self},
                              pre_save=True)
        CorporationTitle.objects.filter(owner=self).exclude(pk__in=titles).delete()

        certificates = handler.autoparse_list(sheet.certificates,
                              Certificate,
                              unique_together=('titleID', 'titleName'),
                              extra_selectors={'owner': self},
                              pre_save=True)
        Certificate.objects.filter(owner=self).exclude(pk__in=certificates).delete()

    def recalculate_skillpoints(self):
        self.skillPoints = Skill.objects.filter(owner=self).aggregate(Sum('skillpoints'))['skillpoints__sum']
        self.save()


class CharacterImplant(models.Model):
    owner = models.ForeignKey(CharacterSheet)
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255)


class JumpClone(models.Model):
    jumpCloneID = models.IntegerField(primary_key=True)
    owner = models.ForeignKey(CharacterSheet)
    typeID = models.IntegerField()
    locationID = models.BigIntegerField()
    cloneName = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        unique_together = ('owner', 'jumpCloneID')


class JumpCloneImplant(models.Model):
    jumpCloneID = models.IntegerField()
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255)
    owner = models.ForeignKey(CharacterSheet)

    class Meta:
        unique_together = ('jumpCloneID', 'typeID')


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
    owner = models.ForeignKey('CharacterSheet')


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

    owner = models.ForeignKey('CharacterSheet')

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

    owner = models.ForeignKey('CharacterSheet')


class Research(models.Model):
    pointsPerDay = models.DecimalField(max_digits=10, decimal_places=2)
    researchStartDate = custom.DateTimeField()
    skillTypeID = models.IntegerField()
    agentID = models.IntegerField()
    remainderPoints = models.DecimalField(max_digits=20, decimal_places=10)

    owner = models.ForeignKey('CharacterSheet')


class AssetList(models.Model):
    items = JsonBField()
    retrieved = custom.DateTimeField()
    owner = models.ForeignKey('CharacterSheet')

    def __unicode__(self):
        return "{0}'s assets ({1})".format(self.owner, self.retrieved)


class Asset(models.Model):
    itemID = models.BigIntegerField()
    quantity = models.BigIntegerField()
    locationID = models.BigIntegerField()
    locationName = models.CharField(max_length=255, blank=True, default='')
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255)
    flag = models.IntegerField()
    singleton = models.BooleanField(default=False)
    rawQuantity = models.IntegerField(default=0)
    path = models.CharField(max_length=255, default='')
    parent_id = models.BigIntegerField(null=True)

    item_value = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)
    item_volume = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)
    container_volume = models.DecimalField(max_digits=30, decimal_places=2, default=0.0)

    owner = models.ForeignKey(CharacterSheet)

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

        if 'rawQuantity' in item:
            self.rawQuantity = item['rawQuantity']

        if 'parent' in item:
            self.parent_id = item['parent']

    def get_contents(self):
        return self.objects.filter(owner=self.owner,
                                   parent_id=self.itemID)

    def get_volume(self):
        if self.singleton:
            return self.item_volume + self.container_volume
        else:
            return self.item_volume

    def compute_statistics(self):
        item = InvType.objects.get(pk=self.typeID)

        if item.marketGroupID < 35000 and item.published:
            index_location = get_location_id(PRICE_INDEX_SYSTEM)
            index_value = MarketItem.objects.get(typeID=self.typeID,
                                                    locationID=index_location.pk).sell_percentile
            self.item_value = self.quantity * index_value

        if not self.singleton and item.groupID in PACKAGED_VOLUME.keys():
            self.item_volume = get_item_packaged_volume(item.groupID, item.pk) * self.quantity
        else:
            self.item_volume = item.volume * self.quantity


    def compute_container_volume(self):
        self.container_volume = 0.0
        if self.singleton:
            contents = self.get_contents()
            for item in contents:
                self.container_volume += item.get_volume()

    def update_from_api(self, item, handler):
        self.compute_statistics()
        self.save()

    class Meta:
        managed = False


class MarketOrder(models.Model):
    orderID = models.BigIntegerField()
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255, null=True)
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

    owner = models.ForeignKey('CharacterSheet')


    def update_from_api(self, sheet, handler):
        self.typeName = InvType.objects.get(pk=self.typeID).typeName
        self.save()


class Medal(models.Model):
    medalID = models.BigIntegerField()
    status = models.CharField(max_length=10)
    issued = custom.DateTimeField()
    issuerID = models.IntegerField()
    reason = models.TextField(blank=True, default='')
    title = models.CharField(max_length=255, null=True)
    corporationID = models.IntegerField(null=True)
    description = models.TextField(blank=True, default='')

    owner = models.ForeignKey('CharacterSheet')


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

    owner = models.ForeignKey('CharacterSheet')

    class Meta:
        verbose_name_plural = "PlanetaryColonies"


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

    owner = models.ForeignKey('CharacterSheet')


class Notification(models.Model):
    typeID = models.IntegerField()
    notificationID = models.IntegerField(db_index=True)
    sentDate = custom.DateTimeField()
    read = models.BooleanField(default=False)
    senderName = models.CharField(max_length=255)
    senderID = models.IntegerField()
    raw_message = models.TextField(null=True)
    parsed_message = models.TextField(null=True)
    broken = models.BooleanField(default=False)

    owner = models.ForeignKey('CharacterSheet')

    def __unicode__(self):
        if self.typeID in api_parser.NOTIFICATION_CODES:
            return u'{0} -> {1}'.format(
                self.senderName,
                api_parser.NOTIFICATION_CODES[self.typeID]
            )
        else:
            return u'{0} -> {1}'.format(
                self.senderName,
                self.typeID
            )


    class Meta:
        unique_together = ('owner', 'notificationID')

    def update_from_api(self, notification, handler):
        self.reparse()

    def reparse(self):
        self.parsed_message = api_parser.parse_notification(
            self.typeID,
            self.raw_message,
            self.notificationID
        )
        self.save()


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

    owner = models.ForeignKey('CharacterSheet')

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

    owner = models.ForeignKey('CharacterSheet')

    class Meta:
        unique_together = ('contract', 'owner', 'rowID')


class ContractBid(models.Model):
    bidID = models.BigIntegerField()
    contractID = models.BigIntegerField()
    bidderID = models.BigIntegerField()
    dateBid = custom.DateTimeField()
    amount = models.DecimalField(max_digits=30, decimal_places=2, null=True)

    owner = models.ForeignKey('CharacterSheet')

    class Meta:
        unique_together = ('bidID', 'contractID', 'owner')


class SkillQueue(models.Model):
    typeID = models.IntegerField()
    endTime = custom.DateTimeField(null=True)
    startTime = custom.DateTimeField(null=True)
    level = models.IntegerField()
    queuePosition = models.IntegerField()
    startSP = models.IntegerField()
    endSP = models.IntegerField()
    typeName = models.CharField(max_length=255, null=True)

    owner = models.ForeignKey('CharacterSheet', related_name='skillQueue')

    def update_from_api(self, sheet, handler):
        self.typeName = InvType.objects.get(pk=self.typeID).typeName
        self.save()




class MailingList(models.Model):
    listID = models.BigIntegerField(primary_key=True)
    displayName = models.CharField(max_length=255)

    owners = models.ManyToManyField('CharacterSheet')



class ContactNotification(models.Model):
    notificationID = models.BigIntegerField()
    senderID = models.IntegerField()
    senderName = models.CharField(max_length=255)
    messageData = models.TextField(blank='', default='')
    sentDate = custom.DateTimeField()

    owner = models.ForeignKey('CharacterSheet')


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('b', 'Buy'),
        ('s', 'Sell')
    )
    TRANSACTION_ISSUER = (
        ('p', 'Personal'),
        ('c', 'Corporation')
    )

    typeID = models.IntegerField(null=True)
    clientTypeID = models.IntegerField(null=True)
    transactionFor = models.CharField(max_length=1, choices=TRANSACTION_ISSUER, blank=True, null=True)
    price = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    clientID = models.BigIntegerField(null=True)
    journalTransactionID = models.BigIntegerField(null=True)
    typeName = models.CharField(max_length=255, blank=True, null=True)
    stationID = models.IntegerField(null=True)
    stationName = models.CharField(max_length=255, blank=True, null=True)
    transactionID = models.BigIntegerField(null=True)
    quantity = models.IntegerField(null=True)
    transactionDateTime = custom.DateTimeField(null=True)
    clientName = models.CharField(max_length=255, blank=True, null=True)
    transactionType = models.CharField(max_length=1, choices=TRANSACTION_TYPES, blank=True, null=True)

    owner = models.ForeignKey('CharacterSheet')

    def client_type(self):
        if self.clientTypeID == 2:
            return 'corp'
        else:
            return 'char'

    def update_from_api(self, transaction, handler):
        if transaction.transactionType == 'buy':
            self.transactionType = 'b'
        else:
            self.transactionType = 's'
        if transaction.transactionFor == 'personal':
            self.transactionFor = 'p'
        else:
            self.transactionFor = 'c'
        self.save()

    class Meta:
        unique_together = ('owner', 'transactionID')


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

    owner = models.ForeignKey('CharacterSheet')


class CorporationTitle(models.Model):
    titleID = models.IntegerField()
    titleName = models.CharField(max_length=255)

    owner = models.ForeignKey('CharacterSheet')


class Certificate(models.Model):
    certificateID = models.IntegerField()

    owner = models.ForeignKey('CharacterSheet')

    class Meta:
        unique_together = ('certificateID', 'owner')




class MailMessage(models.Model):
    messageID = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    senderName = models.CharField(max_length=255, blank=True, null=True)
    senderID = models.IntegerField()
    sentDate = custom.DateTimeField()
    raw_message = models.TextField(null=True)
    parsed_message = models.TextField(null=True)
    broken = models.BooleanField(default=False)
    receivers = JsonBField(default=[], null=True)

    owners = models.ManyToManyField(CharacterSheet)

    def __unicode__(self):
        return self.title

    def populate_receivers(self):
        new_receivers = []
        if not self.receivers:
            self.receivers = []
        for entity in self.receivers:
            if not entity['type'] == 2:
                name = EveName.objects.get_name(entity['id'])
            else:
                try:
                    mailing_list = MailingList.objects.get(pk=entity['id'])
                    name = mailing_list.displayName
                except:
                    name = 'Mailing list {0}'.format(entity['id'])
            new_receivers.append({'name': name,
                               'id': entity['id'],
                               'type': entity['type']})
        self.receivers = new_receivers



    def update_from_api(self, msg, handler):
        def purge(l):
            o = []
            for i in l:
                if i == u'' or not i:
                    continue
                o.append(i)
            return o

        lists = unicode(msg.toListID).split(',')
        characters = unicode(msg.toCharacterIDs).split(',')
        corpalls = unicode(msg.toCorpOrAllianceID).split(',')

        api_receivers = (
            (2, purge(lists)),
            (0, purge(characters)),
            (1, purge(corpalls)),
        )
        recipients = []

        for receiver_type, receiverIDs in api_receivers:
            for receiverID in receiverIDs:
                if not receiver_type == 2:
                    EveName.objects.get_or_create(pk=receiverID)
                recipients.append({'name': receiverID,
                                   'id': receiverID,
                                   'type': receiver_type})
        self.receivers = recipients

        if self.raw_message and not self.parsed_message:
            self.parse_message()

        self.save()

    def parse_message(self):
        self.parsed_message = parse_evemail(self.raw_message)


class SkillInTraining(models.Model):
    trainingStartSP = models.IntegerField(null=True)
    trainingTypeID = models.IntegerField(null=True)
    trainingDestinationSP = models.IntegerField(null=True)
    currentTQTime = custom.DateTimeField(null=True)
    trainingEndTime = custom.DateTimeField(null=True)
    skillInTraining = models.BooleanField(default=True)
    trainingStartTime = custom.DateTimeField(null=True)
    trainingToLevel = models.IntegerField(null=True)
    typeName = models.CharField(max_length=255, null=True)

    owner = models.ForeignKey('CharacterSheet', related_name='skillInTraining')

    def update_from_api(self, sheet, handler):
        try:
            self.typeName = InvType.objects.get(pk=self.trainingTypeID).typeName
            self.save()
        except:
            pass


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

    owner = models.ForeignKey('CharacterSheet')

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

    owner = models.ForeignKey('CharacterSheet')


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

    owner = models.ForeignKey('CharacterSheet')

    class Meta:
        unique_together = ('fromID', 'owner')

@receiver(post_save, sender=CharacterSheet)
def update_apidata(sender, instance=None, created=False, **kwargs):
    if created:
        app.send_task('accounting.update_character_apidata', (instance.pk,))