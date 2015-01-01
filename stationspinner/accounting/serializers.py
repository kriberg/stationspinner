from rest_framework import serializers
from stationspinner.accounting.models import APIKey, Capsuler
from stationspinner.character.models import CharacterSheet
from stationspinner.character.serializers import CharacterSheetShort


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        exclude = ('owner', 'characterID', 'corporationID')


class CapsulerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capsuler
        read_only_fields = ('username', 'email', 'last_login', 'date_joined')
        exclude = ('id', 'password', 'is_superuser', 'is_staff', 'groups', 'is_active',
                   'user_permissions')


class AccountKeySerializer(serializers.ModelSerializer):
    account_characters = serializers.SerializerMethodField('get_characters')

    def get_characters(self, obj):
        characters = CharacterSheet.objects.filter(owner=obj.owner,
                                                   owner_key=obj)
        return characters.values('name')
    class Meta:
        model = APIKey
        exclude = ('owner', 'characterID', 'corporationID')