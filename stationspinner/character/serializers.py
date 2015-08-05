from rest_framework import serializers
from stationspinner.character.models import CharacterSheet, Skill, \
    SkillInTraining, SkillQueue, Asset, CharacterImplant, \
    JumpClone, JumpCloneImplant, Notification, MailMessage, WalletJournal, \
    WalletTransaction
from stationspinner.sde.models import MapDenormalize
from stationspinner.sde.serializers import RegionSerializer

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        exclude = ('owner', 'published', 'id')

class SkillQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillQueue
        exclude = ('owner',)


class SkillInTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillInTraining
        fields = (
            'trainingStartSP',
            'trainingTypeID',
            'trainingDestinationSP',
            'currentTQTime',
            'trainingEndTime',
            'skillInTraining',
            'trainingStartTime',
            'trainingToLevel',
            'typeName',
            'typeID',
        )


class CharacterImplantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterImplant
        exclude = ('owner',)


class JumpCloneImplantSerializer(serializers.ModelSerializer):
    class Meta:
        model = JumpCloneImplant
        fields = ('typeID', 'typeName')


class JumpCloneSerializer(serializers.ModelSerializer):
    jumpCloneImplants = JumpCloneImplantSerializer(many=True)
    class Meta:
        model = JumpClone
        fields = ('location', 'jumpCloneImplants')


class CharacterSheetListSerializer(serializers.ModelSerializer):
    skillInTraining = SkillInTrainingSerializer(many=True)
    class Meta:
        model = CharacterSheet
        exclude = ('owner', 'enabled', 'owner_key')


class CharacterSheetShortListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterSheet
        fields = ('name', 'characterID')


class CharacterImplantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterImplant
        fields = ('typeID', 'typeName')


class CharacterSheetSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)
    skillQueue = SkillQueueSerializer(many=True)
    skillInTraining = SkillInTrainingSerializer(many=True)
    implants = CharacterImplantSerializer(many=True)
    jumpClones = JumpCloneSerializer(many=True)

    class Meta:
        model = CharacterSheet
        fields = (
            'characterID',
            'name',
            'corporationID',
            'corporationName',
            'bloodLine',
            'factionID',
            'factionName',
            'allianceID',
            'allianceName',
            'ancestry',
            'balance',
            'DoB',
            'gender',
            'race',
            'cloneJumpDate',
            'freeRespecs',
            'lastRespecDate',
            'lastTimedRespec',
            'freeSkillPoints',
            'homeStationID',
            'homeStation',
            'jumpActivation',
            'jumpFatigue',
            'jumpLastUpdate',
            'remoteStationDate',
            'skillPoints',
            'charisma',
            'perception',
            'intelligence',
            'memory',
            'willpower',
            'skills',
            'skillQueue',
            'skillInTraining',
            'implants',
            'jumpClones',
        )


class CharacterSheetShort(serializers.ModelSerializer):
    class Meta:
        model = CharacterSheet
        fields = ('characterID', 'name', 'corporationName', 'allianceName')


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = (
            'itemID',
            'quantity',
            'locationName',
            'locationID',
            'typeID',
            'typeName',
            'flag',
            'singleton',
            'rawQuantity',
            'item_value',
            'item_volume',
            'container_value',
            'container_volume'
        )


class NotificationSerializer(serializers.ModelSerializer):
    owner = CharacterSheetShort(many=False)
    class Meta:
        model = Notification
        exclude = ('owner', 'notificationID', 'senderID', 'broken')


class MailMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailMessage
        fields = ('messageID', 'title', 'senderName', 'parsed_message', 'sentDate', 'recipients')


class ShortformCorporationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterSheet
        fields = ('corporationID', 'corporationName')


class ShortformAllianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterSheet
        fields = ('allianceID', 'allianceName')

class WalletTransactionSerializer(serializers.ModelSerializer):
    client_type = serializers.CharField()
    class Meta:
        model = WalletTransaction
        fields = ('transactionDateTime', 'transactionFor', 'transactionType',
                  'typeName', 'stationName', 'quantity', 'price', 'clientName',
                  'client_type')