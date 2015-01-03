from rest_framework import viewsets
from rest_framework.response import Response
from stationspinner.character.serializers import CharacterSheetSerializer, \
    AssetListSerializer, CharacterSheetListSerializer, NotificationSerializer, \
    SkillInTrainingSerializer, MailMessageSerializer
from stationspinner.character.models import CharacterSheet, \
    AssetList, Notification, SkillInTraining, MailMessage
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
                                             enabled=True)

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
    serializer_class = NotificationSerializer
    model = Notification
    permission_classes = [CapsulerPermission]

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
            owner__in=CharacterSheet.objects.filter(owner=self.request.user)
        ).order_by('-sentDate')