from rest_framework import viewsets, response, generics
from stationspinner.libs.drf_extensions import CapsulerPermission
from stationspinner.evemail.models import Mail, MailStatus
from stationspinner.evemail.serializers import MailSerializer, MailStatusSerializer
from stationspinner.settings import EVEMAIL_SEARCH_LANGUAGES

class SearchLanguagesViewset(viewsets.ViewSet):

    def list(self, request):
        return response.Response({'languages': EVEMAIL_SEARCH_LANGUAGES})


class MailViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = MailSerializer
    model = Mail
    permission_classes = [CapsulerPermission]
    #paginate_by = 50
    #max_paginate_by = 200
    #paginate_by_param = 'page_size'

    def get_queryset(self):
        search_query = self.request.query_params.get('search', None)
        query_language = self.request.query_params.get('language', 'english')

        if search_query is not None:
            return Mail.objects.search(search_query, self.request.user, language=query_language)

        return Mail.objects.filter(
            owner=self.request.user
        ).order_by('-sentDate')


class MailStatusViewset(viewsets.ViewSet):
    serializer_class = MailStatusSerializer
    permission_classes = [CapsulerPermission]

    def get_queryset(self):
        return MailStatus.objects.filter(owner=self.request.user)

    def create(self, request):
        messageIDs = request.data.get('messageIDs', [])

        if messageIDs is not None:
            if type(messageIDs) is int:
                messageIDs = [messageIDs]
            mails = self.get_queryset().filter(message__in=messageIDs)
            mails.update(read=True)
            updated =  mails.values_list('message_id', flat=True)
        else:
            updated = []
        return response.Response({'messageIDs': updated})