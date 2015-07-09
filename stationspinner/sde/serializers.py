from rest_framework import serializers
from stationspinner.sde.models import InvType, MapRegion


class InvTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvType
        fields = ('typeName', 'description')


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapRegion
        fields = ('regionID', 'regionName')