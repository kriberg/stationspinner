from rest_framework import serializers
from stationspinner.statistics.models import WalletBalanceEntry, \
    AssetWorthEntry

class CharacterWalletBalanceEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletBalanceEntry
        fields = ('registered', 'value', 'name')


class CorporationWalletBalanceEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletBalanceEntry
        fields = ('registered', 'value', 'description', 'name')


class AssetWorthEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetWorthEntry
        fields = ('owner', 'registered', 'value', 'name')