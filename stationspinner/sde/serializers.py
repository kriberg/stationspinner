from rest_framework import serializers
from stationspinner.sde.models import InvType, MapRegion


class InvTypeSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = InvType
        fields = ('typeName', 'description')


class RegionSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = MapRegion
        fields = ('regionID', 'regionName')