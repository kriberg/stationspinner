from rest_framework import viewsets
from stationspinner.character.serializers import CharacterSheetSerializer
from stationspinner.character.models import CharacterSheet

class CharacterSheetViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = CharacterSheetSerializer
    model = CharacterSheet

    def get_queryset(self):
        return CharacterSheet.objects.filter(
            owner__in=self.request.user.get_active_keys()
        )