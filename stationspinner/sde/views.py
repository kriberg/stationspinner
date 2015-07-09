from django.core.cache import cache
from rest_framework import viewsets, views
from rest_framework.response import Response
from stationspinner.sde.models import InvType, InvMarketGroup
from stationspinner.sde.serializers import InvTypeSerializer

class InvTypeViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvTypeSerializer
    model = InvType

    def list(self, request):
        return Response(None)

    def get_queryset(self):
        return InvType.objects.filter(published=True)

class InvMarketGroupView(views.APIView):
    def get(self, request, format=None):
        market_groups = cache.get(hash('inv_market_groups_2'), None)
        if not market_groups:
            market_groups = InvMarketGroup.objects.get_hierarchy(max_depth=2)
            cache.set(hash('inv_market_groups_2'), market_groups)
        return Response(market_groups)
