from rest_framework import viewsets
from rest_framework.response import Response
from stationspinner.sde.models import InvType
from stationspinner.sde.serializers import InvTypeSerializer

class InvTypeViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvTypeSerializer
    model = InvType

    def list(self, request):
        return Response(None)

    def get_queryset(self):
        return InvType.objects.filter(published=True)