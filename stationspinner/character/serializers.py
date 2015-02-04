from rest_framework import serializers
from stationspinner.character.models import CharacterSheet, Skill, \
    SkillInTraining, SkillQueue, AssetList, Asset, CharacterImplant, \
    JumpClone, JumpCloneImplant, Notification, MailMessage


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        exclude = ('owner',)


class SkillQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillQueue
        exclude = ('owner',)


class SkillInTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillInTraining
        exclude = ('owner',)


class CharacterImplantSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterImplant
        exclude = ('owner',)


class JumpCloneSerializer(serializers.ModelSerializer):
    class Meta:
        model = JumpClone
        exclude = ('owner',)


class JumpCloneImplantSerializer(serializers.ModelSerializer):
    class Meta:
        model = JumpCloneImplant
        exclude = ('owner',)


class CharacterSheetListSerializer(serializers.ModelSerializer):
    skillInTraining = SkillInTrainingSerializer(many=True)
    class Meta:
        model = CharacterSheet
        exclude = ('owner', 'enabled', 'owner_key')

class CharacterSheetSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)
    skillQueue = SkillQueueSerializer(many=True)
    skillInTraining = SkillInTrainingSerializer(many=True)

    class Meta:
        model = CharacterSheet
        exclude = ('owner', 'enabled', 'owner_key')


class CharacterSheetShort(serializers.ModelSerializer):
    class Meta:
        model = CharacterSheet
        fields = ('characterID', 'name', 'corporationName', 'allianceName')


class AssetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetList
        exclude = ('owner',)

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        exclude = ('owner','typeID', 'locationID', 'itemID')


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