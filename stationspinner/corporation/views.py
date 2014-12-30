from rest_framework import viewsets
from rest_framework.response import Response
from stationspinner.corporation.serializers import CorporationSheetSerializer, \
    CorporationSheetListSerializer
from stationspinner.corporation.models import CorporationSheet
from stationspinner.libs.rest_permissions import CapsulerPermission


class CorporationSheetViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = CorporationSheetSerializer
    model = CorporationSheet
    permission_classes = [CapsulerPermission]

    def list(self, request):
        serializer = CorporationSheetListSerializer(
            self.get_queryset(),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def get_queryset(self):
        return CorporationSheet.objects.filter(owner=self.request.user, enabled=True)