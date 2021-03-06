from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.contrib.postgres.fields import JSONField
from stationspinner.accounting.models import APIKey, Capsuler
from stationspinner.universe.models import EveName
from stationspinner.libs import fields as custom, api_parser
from stationspinner.libs.api_parser import parse_evemail
from stationspinner.sde.models import InvType, InvGroup
from django.db.models.signals import post_save
from django.dispatch import receiver
from stationspinner.celery import app
from stationspinner.libs.pragma import get_item_packaged_volume, \
    PACKAGED_VOLUME, get_location_name, UnknownPackagedItem, get_location, \
    get_location_regionID, get_location_regionName, \
    get_location_solarSystemID, get_location_solarSystemName
from celery.utils.log import get_task_logger
from django.db import connections

log = get_task_logger(__name__)


class Skill(models.Model):
    skillpoints = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255, null=True)
    published = models.BooleanField(default=True)
    skill_group = models.CharField(max_length=50, null=True)

    owner = models.ForeignKey('CharacterSheet', related_name='skills')

    def update_from_api(self, data, handler):
        try:
            skill = InvType.objects.get(pk=self.typeID)
            self.typeName = skill.typeName
            self.skill_group = skill.group.groupName
        except InvType.DoesNotExist:
            self.typeName = "Unknown skill {}".format(self.typeID)
            self.skill_group = 'Unknown'

        self.save()

    class Meta(object):
        unique_together = ('typeID', 'owner')


class CharacterSheetManager(models.Manager):
    def filter_valid(self, characterIDs, capsuler):
        valid = self.filter(pk__in=characterIDs, owner=capsuler).values_list('characterID', flat=True)
        invalid = list(set(characterIDs) - set(valid))
        return valid, invalid


class CharacterSheet(models.Model):
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    owner_key = models.ForeignKey(APIKey, null=True)
    owner = models.ForeignKey(Capsuler)
    enabled = models.BooleanField(default=False)

    # From the api
    characterID = models.IntegerField(primary_key=True)  # auto
    name = models.CharField(max_length=255)  # auto
    corporationID = models.IntegerField()  # auto
    corporationName = models.CharField(max_length=255)  # auto
    bloodLine = models.CharField(max_length=50)  # auto
    factionID = models.IntegerField(null=True, default=None)  # auto
    factionName = models.CharField(max_length=100, null=True, default=None)  # auto
    allianceName = models.CharField(max_length=255, blank=True, null=True, default=None)  # auto
    ancestry = models.CharField(max_length=100)  # auto
    balance = models.DecimalField(max_digits=30, decimal_places=2, null=True)  # auto
    DoB = custom.DateTimeField()  # auto
    gender = models.CharField(max_length=6, choices=GENDER)  # auto
    race = models.CharField(max_length=20)  # auto
    allianceID = models.IntegerField(null=True)  # auto
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

    objects = CharacterSheetManager()

    def homeStation(self):
        return get_location_name(self.homeStationID)

    def __unicode__(self):
        return self.name

    def update_from_api(self, sheet, handler):
        handler.autoparse(sheet, self, exclude=('skills',
                                                'jumpClones',
                                                'jumpCloneImplants',
                                                'implants'))
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
                                                unique_together=('jumpCloneID', 'typeID'),
                                                extra_selectors={'owner': self},
                                                owner=self,
                                                pre_save=False)
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
    owner = models.ForeignKey(CharacterSheet, related_name='implants')
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255)


class JumpClone(models.Model):
    jumpCloneID = models.BigIntegerField(primary_key=True)
    owner = models.ForeignKey(CharacterSheet, related_name='jumpClones')
    typeID = models.IntegerField()
    locationID = models.BigIntegerField()
    cloneName = models.CharField(max_length=255, blank=True, default='')

    def location(self):
        location = get_location_name(self.locationID)
        if location == self.locationID:
            try:
                location = ItemLocationName.objects.get(itemID=self.locationID)
            except ItemLocationName.DoesNotExist:
                return location
        return location

    def jumpCloneImplants(self):
        return JumpCloneImplant.objects.filter(jumpCloneID=self.jumpCloneID)

    class Meta(object):
        unique_together = ('owner', 'jumpCloneID')


class JumpCloneImplant(models.Model):
    jumpCloneID = models.BigIntegerField()
    typeID = models.IntegerField()
    typeName = models.CharField(max_length=255)
    owner = models.ForeignKey(CharacterSheet)

    class Meta(object):
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

    class Meta(object):
        unique_together = ('owner', 'eventID')


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

    class Meta(object):
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

    class Meta(object):
        unique_together = ('owner', 'listType', 'contactID')


class Research(models.Model):
    pointsPerDay = models.DecimalField(max_digits=10, decimal_places=2)
    researchStartDate = custom.DateTimeField()
    skillTypeID = models.IntegerField()
    agentID = models.IntegerField()
    remainderPoints = models.DecimalField(max_digits=20, decimal_places=10)

    owner = models.ForeignKey('CharacterSheet')

    class Meta(object):
        unique_together = ('owner', 'agentID')


class AssetList(models.Model):
    items = JSONField()
    retrieved = custom.DateTimeField()
    owner = models.ForeignKey('CharacterSheet')

    def __unicode__(self):
        return "{0}'s assets ({1})".format(self.owner, self.retrieved)


class AssetManager(models.Manager):
    def search(self, characterIDs, query):
        return self.raw('''
        SELECT
            *,
            ts_rank(search_tokens, plainto_tsquery(%(query)s)) as relevancy
        FROM
            character_asset
        WHERE
            owner_id IN %(characterIDs)s AND
            search_tokens @@ plainto_tsquery(%(query)s)
        ORDER BY
            relevancy DESC;
        ''', {
            'query': query,
            'characterIDs': tuple(characterIDs)
        })

    def summarize(self, characterIDs):
        with connections['default'].cursor() as cursor:
            cursor.execute('''
            SELECT COALESCE(
                ARRAY_TO_JSON(ARRAY_AGG(ROW_TO_JSON(summary))),
                '[]'
            )
            FROM
              (SELECT
                 c.name,
                 a.owner_id AS "characterID",
                 sum(a.item_value)
               FROM
                 character_asset a,
                 character_charactersheet c
               WHERE
                 a.owner_id IN %(characterIDs)s AND
                 c."characterID" = a.owner_id AND
                 c.enabled = TRUE
               GROUP BY c.name, a.owner_id
               ORDER BY sum DESC) summary;
            ''', {'characterIDs': tuple(characterIDs)})

            return cursor.fetchone()[0]

    def net_worth(self, character):
        with connections['default'].cursor() as cursor:
            cursor.execute('''
            SELECT
               sum(a.item_value)
           FROM
             character_asset a
           WHERE
             a.owner_id = %(characterID)s
            ''', {'characterID': character.pk})

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

    owner = models.ForeignKey(CharacterSheet)

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
                                   'owner': self.owner.name
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

    owner = models.ForeignKey('CharacterSheet')

    def update_from_api(self, sheet, handler):
        try:
            self.typeName = InvType.objects.get(pk=self.typeID).typeName
        except InvType.DoesNotExist:
            log.warning('TypeID {0} does not exist.'.format(self.typeID))
            self.typeName = self.typeID
        self.save()

    class Meta(object):
        unique_together = ('owner', 'orderID')


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

    class Meta(object):
        unique_together = ('owner', 'medalID')



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

    class Meta(object):
        verbose_name_plural = "PlanetaryColonies"
        unique_together = ('owner', 'planetID')


class WalletJournal(models.Model):
    taxReceiverID = models.CharField(max_length=255, blank=True, null=True)
    argName1 = models.CharField(max_length=255, blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    date = custom.DateTimeField()
    refTypeID = models.IntegerField(db_index=True)
    refID = models.BigIntegerField()
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

    class Meta(object):
        unique_together = ('refID', 'owner')


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

    class Meta(object):
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

    class Meta(object):
        unique_together = ('owner', 'contractID')


class ContractItem(models.Model):
    contract = models.ForeignKey(Contract)
    rowID = models.BigIntegerField()
    typeID = models.IntegerField()
    quantity = models.BigIntegerField()
    rawQuantity = models.IntegerField(null=True)
    singleton = models.BooleanField(default=False)
    included = models.BooleanField(default=True)

    owner = models.ForeignKey('CharacterSheet')

    class Meta(object):
        unique_together = ('contract', 'owner', 'rowID')


class ContractBid(models.Model):
    bidID = models.BigIntegerField()
    contractID = models.BigIntegerField()
    bidderID = models.BigIntegerField()
    dateBid = custom.DateTimeField()
    amount = models.DecimalField(max_digits=30, decimal_places=2, null=True)

    owner = models.ForeignKey('CharacterSheet')

    class Meta(object):
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
        try:
            self.typeName = InvType.objects.get(pk=self.typeID).typeName
        except InvType.DoesNotExist:
            self.typeName = self.typeID
        self.save()

    class Meta(object):
        unique_together = ('owner', 'typeID', 'level')


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

    class Meta(object):
        unique_together = ('owner', 'notificationID')


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

    class Meta(object):
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

    class Meta(object):
        unique_together = ('owner', 'roleID', 'location')


class CorporationTitle(models.Model):
    titleID = models.IntegerField()
    titleName = models.CharField(max_length=255)

    owner = models.ForeignKey('CharacterSheet')

    class Meta(object):
        unique_together = ('owner', 'titleID')


class Certificate(models.Model):
    certificateID = models.IntegerField()

    owner = models.ForeignKey('CharacterSheet')

    class Meta(object):
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
    receivers = JSONField(default=[], null=True)

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

    def typeID(self):
        return self.trainingTypeID

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

    owner = models.ForeignKey('CharacterSheet')

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
    blueprintTypeID = models.IntegerField(null=True)
    timeInSeconds = models.IntegerField()
    productTypeID = models.IntegerField(null=True)
    completedDate = custom.DateTimeField(null=True)
    completedCharacterID = models.IntegerField(null=True)
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

    owner = models.ForeignKey('CharacterSheet')

    class Meta(object):
        unique_together = ('owner', 'jobID')


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

    class Meta(object):
        unique_together = ('fromID', 'owner')


class ItemLocationName(models.Model):
    itemID = models.BigIntegerField(primary_key=True)
    itemName = models.CharField(max_length=255)
    owner = models.ForeignKey(CharacterSheet)
    x = models.BigIntegerField(default=0)
    y = models.BigIntegerField(default=0)
    z = models.BigIntegerField(default=0)

    def __unicode__(self):
        return self.itemName

    class Meta(object):
        unique_together = ('itemID', 'owner')





@receiver(post_save, sender=CharacterSheet)
def update_apidata(sender, instance=None, created=False, **kwargs):
    if created:
        app.send_task('accounting.update_character_apidata', (instance.pk,))
