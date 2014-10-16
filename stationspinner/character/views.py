from rest_framework import viewsets
from stationspinner.character.serializers import CharacterSheetSerializer, \
    AssetListSerializer
from stationspinner.character.models import CharacterSheet, \
    AssetList

class CharacterSheetViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = CharacterSheetSerializer
    model = CharacterSheet

    def get_queryset(self):
        return CharacterSheet.objects.filter(
            owner__in=self.request.user.get_active_keys()
        )

class AssetListViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssetListSerializer
    model = AssetList

    def get_queryset(self):
        return AssetList.objects.filter(
            owner=self.request.user
        )