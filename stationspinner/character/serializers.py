from rest_framework import serializers
from stationspinner.character.models import CharacterSheet, Skill, \
    SkillInTraining, SkillQueue, AssetList


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


class CharacterSheetSerializer(serializers.HyperlinkedModelSerializer):
    skills = SkillSerializer(many=True)
    skillQueue = SkillQueueSerializer(many=True)
    skillInTraining = SkillInTrainingSerializer()

    class Meta:
        model = CharacterSheet
        exclude = ('owner', 'enabled', 'owner_key')


class AssetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetList
        exclude = ('owner',)