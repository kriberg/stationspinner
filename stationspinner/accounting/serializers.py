from rest_framework import serializers
from stationspinner.accounting.models import APIKey, Capsuler
from stationspinner.character.models import CharacterSheet
from stationspinner.corporation.models import CorporationSheet


class APIKeySerializer(serializers.ModelSerializer):
    associated_characters = serializers.SerializerMethodField('get_characters', read_only=True)
    associated_corporations = serializers.SerializerMethodField('get_corporations', read_only=True)

    def get_characters(self, obj):
        characters = CharacterSheet.objects.filter(owner=obj.owner,
                                                   owner_key=obj)
        return characters.values('name', 'characterID')

    def get_corporations(self, obj):
        corporations = CorporationSheet.objects.filter(owner=obj.owner,
                                                       owner_key=obj)
        return corporations.values('corporationName', 'corporationID')

    class Meta:
        model = APIKey
        exclude = ('owner', 'characterID', 'corporationID')
        read_only_fields = ('expired', 'expires', 'type', 'accessMask', 'id')


class CapsulerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capsuler
        read_only_fields = ('username', 'email', 'last_login', 'date_joined')
        exclude = ('id', 'password', 'is_superuser', 'is_staff', 'groups', 'is_active',
                   'user_permissions')

