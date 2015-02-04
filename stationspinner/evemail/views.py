from rest_framework import viewsets, response
from stationspinner.libs.drf_extensions import CapsulerPermission
from stationspinner.evemail.models import Mail
from stationspinner.evemail.serializers import MailSerializer
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
        search_query = self.request.QUERY_PARAMS.get('search', None)
        query_language = self.request.QUERY_PARAMS.get('language', 'english')

        if search_query is not None:
            return Mail.objects.search(search_query, self.request.user, language=query_language)

        return Mail.objects.filter(
            owner=self.request.user
        ).order_by('-sentDate')