from rest_framework import serializers
from stationspinner.character.models import CharacterSheet

class CharacterSheetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CharacterSheet
        exclude = ('owner', 'enabled')
