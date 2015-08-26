from django.core.cache import cache
from rest_framework import views
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from stationspinner.character.serializers import CharacterSheetSerializer, \
    AssetSerializer, CharacterSheetListSerializer, NotificationSerializer, \
    MailMessageSerializer, ShortformAllianceSerializer, \
    CharacterSheetShortListSerializer, ShortformCorporationSerializer, \
    WalletTransactionSerializer
from stationspinner.character.models import CharacterSheet, \
    Asset, Notification, MailMessage, WalletTransaction, \
    WalletJournal
from stationspinner.libs.drf_extensions import CapsulerPermission
from stationspinner.libs.assethandlers import CharacterAssetHandler
from datetime import datetime



class CharacterSheetViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = CharacterSheetSerializer
    model = CharacterSheet
    permission_classes = [CapsulerPermission]

    def list(self, request):
        if request.query_params.get('short', False):
            serializer = CharacterSheetShortListSerializer(
                self.get_queryset(),
                many=True,
                context={'request': request}
            )
        else:
            serializer = CharacterSheetListSerializer(
                self.get_queryset(),
                many=True,
                context={'request': request}
            )
        return Response(serializer.data)

    def get_queryset(self):
        return CharacterSheet.objects.filter(owner=self.request.user,
                                             enabled=True).order_by('-skillPoints')

class NotificationViewset(viewsets.ReadOnlyModelViewSet):
    class NotificationPagination(PageNumberPagination):
        page_size = 10
        ordering = '-sentDate'
    serializer_class = NotificationSerializer
    model = Notification
    permission_classes = [CapsulerPermission]
    pagination_class = NotificationPagination

    def get_queryset(self):
        return Notification.objects.filter(
            owner__in=CharacterSheet.objects.filter(owner=self.request.user)
        ).order_by('-sentDate')


class MailMessageViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = MailMessageSerializer
    model = MailMessage
    permission_classes = [CapsulerPermission]

    def get_queryset(self):
        return MailMessage.objects.filter(
            owners__in=CharacterSheet.objects.filter(owner=self.request.user)
        ).order_by('-sentDate')


class DistinctAllianceViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShortformAllianceSerializer
    permission_classes = [CapsulerPermission]
    model = CharacterSheet

    def get_queryset(self):
        characters = CharacterSheet.objects.filter(owner=self.request.user)

        return characters.exclude(allianceID=None) \
            .exclude(allianceID=0) \
            .distinct('allianceID', 'allianceName') \
            .values('allianceID', 'allianceName') \
            .order_by('allianceName')


class DistinctCorporationViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShortformCorporationSerializer
    permission_classes = [CapsulerPermission]
    model = CharacterSheet

    def get_queryset(self):
        characters = CharacterSheet.objects.filter(owner=self.request.user)

        return characters.distinct('corporationID', 'corporationName') \
            .values('corporationID', 'corporationName') \
            .order_by('corporationName')

class WalletTransactionsViewset(viewsets.ReadOnlyModelViewSet):
    class WalletTransactionPagination(PageNumberPagination):
        page_size = 50
        ordering = '-transactionDateTime'

    serializer_class = WalletTransactionSerializer
    permission_classes = [CapsulerPermission]
    model = WalletTransaction
    pagination_class = WalletTransactionPagination

    def get_queryset(self):
        characterID = self.request.query_params.get('characterID', None)

        if characterID is not None:
            try:
                character = CharacterSheet.objects.get(owner=self.request.user,
                                                       characterID=characterID)
            except CharacterSheet.DoesNotExist:
                return []
            return WalletTransaction.objects.filter(owner=character).order_by('-transactionDateTime')
        else:
            return []



class AssetLocationsView(views.APIView):
    permission_classes = [CapsulerPermission]
    handler = CharacterAssetHandler()

    def get(self, request, format=None):
        characterIDs = request.query_params.get('characterIDs', [])
        locationIDs = request.query_params.get('locationIDs', None)
        locationID = request.query_params.get('locationID', None)

        if locationID and not locationIDs:
            locationIDs = locationID

        if locationIDs:
            locationIDs = str(locationIDs).split(',')
        else:
            locationIDs = []

        if len(characterIDs) > 0:
            try:
                characterIDs = str(characterIDs).split(',')
                valid, invalid = CharacterSheet.objects.filter_valid(characterIDs, request.user)
                characterIDs = valid
            except:
                characterIDs = []
            asset_locations = self.handler.get_merged_asset_locations(characterIDs,
                                                                      locationIDs=locationIDs)
        else:
            asset_locations = []

        return Response(asset_locations)


class AssetsView(views.APIView):
    permission_classes = [CapsulerPermission]
    handler = CharacterAssetHandler()

    def get(self, request, format=None):
        characterIDs = request.query_params.get('characterIDs', [])
        locationID = request.query_params.get('locationID', None)
        parentID = request.query_params.get('parentID', None)

        if len(characterIDs) > 0 and locationID:
            try:
                characterIDs = str(characterIDs).split(',')
                valid, invalid = CharacterSheet.objects.filter_valid(characterIDs, request.user)
                characterIDs = valid
            except:
                characterIDs = []

            assets = self.handler.get_location_assets(
                tuple(characterIDs),
                locationID=locationID,
                parent_id=parentID
            )
        else:
            assets = []

        return Response(assets)