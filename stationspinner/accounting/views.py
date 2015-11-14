from django.views.generic import View
from django.contrib.auth import logout
from django.http import HttpResponse
from rest_framework import viewsets, views
from rest_framework.response import Response
from stationspinner.accounting.serializers import APIKeySerializer, \
    CapsulerSerializer
from stationspinner.accounting.models import APIKey, Capsuler
from stationspinner.character.models import SkillInTraining
from stationspinner.universe.models import APICall
from stationspinner.libs.drf_extensions import CapsulerPermission, CapsulerViewset
from stationspinner.celery import app


class APIKeyViewset(CapsulerViewset):
    serializer_class = APIKeySerializer
    model = APIKey
    permission_classes = [CapsulerPermission]

    def get_queryset(self):
        return APIKey.objects.filter(owner=self.request.user)


class RevalidateKeyView(views.APIView):
    permission_classes = [CapsulerPermission]

    def post(self, request):
        id = request.data.get('id', None)
        if id:
            try:
                key = APIKey.objects.get(pk=id, owner=request.user)
            except APIKey.DoesNotExist:
                return Response({'msg': 'No such APIKey.'}, status=404)
            app.send_task('accounting.validate_key', [key.pk])
            return Response({'msg': 'Revalidation queued.'})

        return Response({'msg': 'No such APIKey'}, status=404)


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


class MissingTrainingViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = APIKeySerializer
    model = APIKey
    permission_classes = [CapsulerPermission]

    def get_queryset(self):
        keys_without_training = []
        training_call = APICall.objects.get(name='SkillInTraining')
        account_keys = APIKey.objects.filter(owner=self.request.user,
                                             type='Account')
        for key in account_keys:
            if not key.accessMask & training_call.accessMask > 0:
                continue
            training = SkillInTraining.objects.filter(
                owner__owner=self.request.user,
                owner__owner_key=key,
                skillInTraining=True)
            if training.count() == 0:
                keys_without_training.append(key.pk)

        return APIKey.objects.filter(owner=self.request.user,
                                     pk__in=keys_without_training)