from django.core.cache import cache
from rest_framework import viewsets, views
from rest_framework.response import Response
from stationspinner.corporation.serializers import CorporationSheetSerializer, \
    CorporationSheetListSerializer
from stationspinner.corporation.models import CorporationSheet, Asset
from stationspinner.libs.drf_extensions import CapsulerPermission


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


class AssetLocationsView(views.APIView):
    permission_classes = [CapsulerPermission]

    def get(self, request, format=None):
        corporationID = request.query_params.get('corporationID', None)
        regionID = request.query_params.get('regionID', None)

        if not corporationID:
            return Response([])
        else:
            try:
                corporation = CorporationSheet.objects.get(owner=request.user,
                                                           pk=corporationID)
            except CorporationSheet.DoesNotExist:
                return Response([])


        key = hash(('asset_locations', corporation.pk.__hash__, regionID))
        asset_locations = cache.get(key, None)
        if not asset_locations:
            asset_locations = Asset.objects.get_top_level_locations(corporation.pk, regionID)
            cache.set(key, asset_locations, 1800)

        return Response(asset_locations)