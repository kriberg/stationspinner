from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from stationspinner.accounting.models import Capsuler
import pytz, pycrest, hashlib, os

def _set_crest_data(auth_con, capsuler):
    expires_in_seconds = (datetime.fromtimestamp(auth_con.expires, pytz.UTC) -
                          datetime.now(tz=pytz.UTC)).total_seconds()
    # This sets the token for communication between armada, stationspinner and
    # crest.
    print auth_con.token, expires_in_seconds
    cache.set(auth_con.token,
              {
                  'username': capsuler.username,
                  'refresh_token': auth_con.refresh_token,
                  'expires': auth_con.expires
              },
              timeout=expires_in_seconds)
    return auth_con.token

def login(capsuler, auth_con, state_token):
    key = _set_crest_data(auth_con, capsuler)

    # This sets the state_token which we've sent through the sso and back to us
    # and ties it to the sso token. We only keep this for a short period of
    # time, so it is hard to bruteforce and intercept a connection.

    cache.set(state_token, key, timeout=60)

def deny_login(state_token, reason):
    '''
    If the user is denied access, albeit successfully authenticating from the
    sso, we need to send a message back. We'll stick it into our state token.
    '''
    cache.set(state_token, reason, timeout=60)

def check_login(state_token):
    '''
    Gets messages or token from the cache.
    '''
    auth_data = cache.get(state_token, None)

    if not auth_data:
        # User polled a non-existant token. Very suspicious.
        return None, 403

    if auth_data == 'waiting for sso':
        return {'waiting': True}, 200

    if type(auth_data) is dict and 'error' in auth_data:
        # Login has failed for some reason
        return auth_data['error'], 400

    crest_data = cache.get(auth_data, None)
    if crest_data and 'username' in crest_data:
        # Login has been successful. Delete the state token and send the new
        # token back to the user
        crest_token = auth_data
        cache.delete(state_token)
        return {'token': crest_token,
                'expires': crest_data['expires']}, 200

    return 'Stuck in warp tunnel!', 400


def logout(request):
    auth = get_authorization_header(request).split()
    try:
        token = auth[1].decode()
    except UnicodeError:
        return

    cache.delete(token)

def get_authorized_connection(code):
    eve_sso = pycrest.EVE(client_id=settings.CREST_CLIENTID,
                          api_key=settings.CREST_SECRET_KEY)

    return eve_sso.authorize(code)

def refresh_token(token, capsuler):
    auth_data = cache.get(token, None)
    if not auth_data:
        raise exceptions.AuthenticationFailed('Token has expired.')
    eve_sso = pycrest.EVE(client_id=settings.CREST_CLIENTID,
                          api_key=settings.CREST_SECRET_KEY)

    auth_con = eve_sso.refr_authorize(auth_data['refresh_token'])
    cache.delete(token)
    new_token = _set_crest_data(auth_con, capsuler)
    return new_token

def get_authorization_token():
    token = hashlib.sha1(os.urandom(128)).hexdigest()
    cache.set(token, 'waiting for sso', timeout=60*60*8)
    return token


class CrestAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        token_data = cache.get(token, None)
        if not token_data:
            raise exceptions.AuthenticationFailed('Invalid token.')

        try:
            capsuler = Capsuler.objects.get(username=token_data['username'])
        except Capsuler.DoesNotExist:
             raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        if not capsuler.is_active:
             raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (capsuler, token)


    def authenticate_header(self, request):
        return 'Token'