from django.http import HttpResponse
from rest_framework import views, viewsets
from rest_framework.response import Response
from stationspinner.libs.drf_extensions import CapsulerPermission, ValidatedIDsMixin
from stationspinner.statistics.models import AssetWorthEntry, \
    WalletBalanceEntry
from stationspinner.statistics.serializers import \
    CharacterWalletBalanceEntrySerializer, \
    CorporationWalletBalanceEntrySerializer, \
    AssetWorthEntrySerializer
from stationspinner.character.models import CharacterSheet
from stationspinner.corporation.models import CorporationSheet


class CharacterAssetSummaryView(ValidatedIDsMixin, views.APIView):
    permission_classes = [CapsulerPermission]
    serializer_class = AssetWorthEntrySerializer
    validation_class = CharacterSheet
    validation_lookup_key = 'characterIDs'

    def post(self, request, format=None):
        valid, invalid = self.filter_valid_IDs(request.data, request.user)

        if len(valid) == 0:
            summary = []
        else:
            summary = AssetWorthEntry.objects.get_latest(valid)

        serializer = self.serializer_class(summary, many=True)
        return Response(serializer.data)


class CorporationAssetSummaryView(ValidatedIDsMixin, views.APIView):
    permission_classes = [CapsulerPermission]
    serializer_class = AssetWorthEntrySerializer
    validation_class = CorporationSheet
    validation_lookup_key = 'corporationIDs'

    def post(self, request, format=None):
        valid, invalid = self.filter_valid_IDs(request.data, request.user)

        if len(valid) == 0:
            summary = []
        else:
            summary = AssetWorthEntry.objects.get_latest(valid)

        serializer = self.serializer_class(summary, many=True)
        return Response(serializer.data)


class CharacterWalletBalanceView(ValidatedIDsMixin, views.APIView):
    permission_classes = [CapsulerPermission]
    serializer_class = CharacterWalletBalanceEntrySerializer
    validation_class = CharacterSheet
    validation_lookup_key = 'characterIDs'

    def post(self, request, format=None):
        valid, invalid = self.filter_valid_IDs(request.data. request.user)

        if len(valid) == 0:
            summary = []
        else:
            summary = WalletBalanceEntry.objects.get_latest(valid)

        serializer = self.serializer_class(summary, many=True)
        return Response(serializer.data)


class CorporationWalletBalanceView(ValidatedIDsMixin, views.APIView):
    permission_classes = [CapsulerPermission]
    serializer_class = CorporationWalletBalanceEntrySerializer
    validation_class = CorporationSheet
    validation_lookup_key = 'corporationIDs'

    def post(self, request, format=None):
        valid, invalid = self.filter_valid_IDs(request.data, request.user)

        if len(valid) == 0:
            summary = []
        else:
            summary = WalletBalanceEntry.objects.get_latest(valid)

        serializer = self.serializer_class(summary, many=True)
        return Response(serializer.data)


class CharacterAssetWorthView(ValidatedIDsMixin, views.APIView):
    permission_classes = [CapsulerPermission]
    validation_class = CharacterSheet
    validation_lookup_key = 'characterIDs'

    def post(self, request, format=None):
        valid, invalid = self.filter_valid_IDs(request.data,
                                               request.user)
        entries = AssetWorthEntry.objects.get_latest_range(valid, 365)
        return HttpResponse(entries)
