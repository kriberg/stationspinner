from rest_framework import serializers
from stationspinner.sde.models import InvType


class InvTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvType
        fields = ('typeName', 'description')