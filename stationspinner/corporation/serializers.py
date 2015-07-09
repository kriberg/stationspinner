from rest_framework import serializers
from stationspinner.corporation.models import CorporationSheet

class CorporationSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporationSheet
        exclude = ('owner', 'owner_key', 'enabled')



class CorporationSheetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporationSheet
        fields = ('corporationID', 'corporationName', 'allianceID', 'allianceName')
        #exclude = (
        #    'owner', 'owner_key', 'enabled', 'description', 'memberLimit', 'taxRate', 'factionID', 'ceoName',
        #    'ceoID', 'stationName', 'stationID', 'memberCount', 'shares', 'url'
        #)