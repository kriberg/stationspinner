from rest_framework import serializers
from stationspinner.accounting.models import APIKey, Capsuler


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
