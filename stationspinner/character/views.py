from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from stationspinner.character.serializers import CharacterSheetSerializer, \
    AssetListSerializer, CharacterSheetListSerializer, NotificationSerializer, \
    SkillInTrainingSerializer, MailMessageSerializer, ShortformAllianceSerializer, \
    ShortformCorporationSerializer, WalletTransactionSerializer
from stationspinner.character.models import CharacterSheet, \
    AssetList, Notification, SkillInTraining, MailMessage, WalletTransaction, \
    WalletJournal
from stationspinner.libs.drf_extensions import CapsulerPermission


class CharacterSheetViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = CharacterSheetSerializer
    model = CharacterSheet
    permission_classes = [CapsulerPermission]

    def list(self, request):
        serializer = CharacterSheetListSerializer(
            self.get_queryset(),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def get_queryset(self):
        return CharacterSheet.objects.filter(owner=self.request.user,
                                             enabled=True).order_by('-skillPoints')

#class AssetListViewset(viewsets.ReadOnlyModelViewSet):
#    serializer_class = AssetListSerializer
#    model = AssetList
#    permission_classes = [CapsulerPermission]
#
#    def get_queryset(self):
#        return AssetList.objects.filter(
#            owner=self.request.user
#        )


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
