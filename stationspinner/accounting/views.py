from django.views.generic import View
from django.conf import settings
from django.http import HttpResponse
from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from stationspinner.accounting.authentication import login, logout, \
    get_authorized_connection, get_authorization_token, deny_login, \
    check_login, refresh_token
from stationspinner.accounting.serializers import APIKeySerializer, \
    CapsulerSerializer
from stationspinner.accounting.models import APIKey, Capsuler
from stationspinner.character.models import SkillInTraining
from stationspinner.universe.models import APICall
from stationspinner.libs.drf_extensions import CapsulerPermission, CapsulerViewset
from stationspinner.celery import app
import importlib
from pycrest.errors import APIException as CrestAPIException


class ObtainAuthTokenView(views.APIView):
    '''
    This view creates a auth token for creating a channel between the browser
    and the backend which later can be used to fetch the crest authenticated
    token which then again is used as the authentication token between armada
    and stationspinner.
    '''
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        token = get_authorization_token()
        return Response({
            'clientID': settings.CREST_CLIENTID,
            'callbackURL': settings.CREST_CALLBACK_URL,
            'authToken': token
        })


class CheckAuthTokenView(views.APIView):
    '''
    This view is used for polling crest auth through the generated auth token.
    '''
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        state_token = request.query_params.get('authToken', None)
        if not state_token or len(state_token) != 40:
            return Response('Illegal token', status=400)

        data, status_code = check_login(state_token)

        return Response(data, status=status_code)


class RefreshAuthTokenView(views.APIView):
    '''
    This view refreshes the CREST token and
    '''
    permission_classes = [CapsulerPermission]

    def get(self, request, *args, **kwargs):
        crest_auth = self.get_authenticators()[0]
        capsuler, token = crest_auth.authenticate(request)
        token = refresh_token(token, capsuler)
        return Response({
            'token': token
        })

class APIKeyViewset(CapsulerViewset):
    serializer_class = APIKeySerializer
    model = APIKey
    permission_classes = [CapsulerPermission]

    def get_queryset(self):
        return APIKey.objects.filter(owner=self.request.user)


class RevalidateKeyView(views.APIView):
    permission_classes = [CapsulerPermission]

    def post(self, request):
        apikey_pk = request.data.get('id', None)
        if apikey_pk:
            try:
                key = APIKey.objects.get(pk=apikey_pk, owner=request.user)
            except APIKey.DoesNotExist:
                return Response({'msg': 'No such APIKey.'}, status=404)
            app.send_task('accounting.validate_key', [key.pk])
            return Response({'msg': 'Revalidation queued.'})

        return Response({'msg': 'No such APIKey'}, status=404)


class CapsulerViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CapsulerSerializer
    model = Capsuler
    lookup_field = 'username'

    def list(self, request, *args, **kwargs):
        obj = self.get_queryset().get(pk=self.request.user.pk)
        serializer = self.serializer_class(obj)
        return Response(serializer.data)

    def get_queryset(self):
        return Capsuler.objects.filter(pk=self.request.user.pk)


class LoginView(views.APIView):
    login_template = '''
    <script type="text/javascript">
        window.close();
    </script>
    '''
    def authorize_characterID(self, characterID):
        if not hasattr(settings, 'ACCOUNT_CREATION_FILTERS'):
            return True

        filters = settings.ACCOUNT_CREATION_FILTERS
        for filter_class in filters:
            module_name = '.'.join(filter_class.split('.')[:-1])
            filter_name = filter_class.split('.')[-1]
            filter_module = importlib.import_module(module_name)
            filter = getattr(filter_module, filter_name)()
            if filter.authorize(characterID):
                return True
        return False

    def get(self, request, *args, **kwargs):
        code = request.query_params.get('code', None)
        state_token = request.query_params.get('state', None)
        if not code or not state_token:
            return Response({'error': 'Unauthorized token'}, status=401)

        try:
            auth_con = get_authorized_connection(code)
        except CrestAPIException:
            deny_login(state_token, {'error': 'Unauthorized token'})
            return Response({'error': 'Unauthorized token'}, status=401)

        userdata = auth_con.whoami()

        if not self.authorize_characterID(userdata['CharacterID']):
            deny_login(state_token, {'error': 'Unauthorized character'})
            return Response({'error': 'Unauthorized character'}, status=403)

        if Capsuler.objects.filter(username=userdata['CharacterName']).count() == 0:
            capsuler, created = Capsuler.objects.get_or_create(username=userdata['CharacterName'],
                                                               owner_hash=userdata['CharacterOwnerHash'])
        else:
            try:
                capsuler = Capsuler.objects.get(username=userdata['CharacterName'])

                if capsuler.owner_hash is None:
                    capsuler.owner_hash = userdata['CharacterOwnerHash']
                    capsuler.save()
                if capsuler.owner_hash != userdata['CharacterOwnerHash']:
                    # The character has changed account, so we will deny access
                    # and deactivate the account
                    capsuler.is_active = False
                    capsuler.save()
                    deny_login(state_token, {'error': 'Unauthorized character'})
                    return Response({'error': 'Unauthorized character'}, status=403)

            except Capsuler.DoesNotExist:
                deny_login(state_token, {'error': 'Unauthorized character'})
                return Response({'error': 'Unauthorized character'}, status=403)

        login(capsuler, auth_con, state_token)
        return HttpResponse(self.login_template)


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return HttpResponse('Safe log-out completed.')


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