from django.views.generic import View
from django.contrib.auth import logout
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
from stationspinner.accounting.serializers import APIKeySerializer, \
    CapsulerSerializer
from stationspinner.accounting.models import APIKey, Capsuler
from stationspinner.libs.rest_permissions import CapsulerPermission


class APIKeyViewset(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    model = APIKey
    permission_classes = [CapsulerPermission]

    def get_queryset(self):
        return APIKey.objects.filter(owner=self.request.user)


class CapsulerViewset(viewsets.ModelViewSet):
    serializer_class = CapsulerSerializer
    model = Capsuler

    def list(self, request):
        serializer = CapsulerSerializer(self.get_queryset(),
                                        context={'request': request})
        return Response(serializer.data)

    def get_queryset(self):
        return Capsuler.objects.get(username=self.request.user.username)


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return HttpResponse('')