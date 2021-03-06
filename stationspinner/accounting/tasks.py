from stationspinner.celery import app
from celery import group, chain
from datetime import datetime
from django.db.models import Q
from traceback import format_exc
from pytz import UTC

from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.libs.pragma import get_current_time
from stationspinner.libs.eveapi.eveapi import AuthenticationError
from stationspinner.accounting.models import Capsuler, APIKey, APIUpdate
from stationspinner.accounting.signals import accounting_new_character, \
    accounting_new_corporation
from stationspinner.character.models import CharacterSheet
from stationspinner.corporation.models import CorporationSheet
from stationspinner.universe.models import APICall
from stationspinner.character.tasks import API_MAP as character_tasks, fetch_charactersheet
from stationspinner.corporation.tasks import API_MAP as corporation_tasks, fetch_corporationsheet

from celery.utils.log import get_task_logger

log = get_task_logger(__name__)

@app.task(name='accounting.update_capsulers', max_retries=0)
def update_capsulers():
    chain(update_capsuler_keys.s(), update_all_sheets.s(), update_all_apidata.s())()

@app.task(name='accounting.update_capsuler_keys', max_retries=0)
def update_capsuler_keys(*args, **kwargs):
    capsulers = Capsuler.objects.filter(is_active=True)

    active_keys = APIKey.objects.filter(owner__in=capsulers)
    log.info('Validating {0} keys'.format(active_keys.count()))
    for key in active_keys:
        validate_key.s(key.pk).apply_async(queue='transient')


def queue_capsuler_keys(capsuler):
    log.info('Refreshing capsuler "{0}" keys'.format(capsuler.username))

    keys = APIKey.objects.filter(owner=capsuler)
    if keys.count() == 0:
        return None

    return validate_key.map([apikey.pk for apikey in keys])

@app.task(name='accounting.update_apikey_sheets', max_retries=0)
def update_apikey_sheets(apikey_pk):
    tasks = []
    try:
        key = APIKey.objects.get(pk=apikey_pk, expired=False)
    except APIKey.DoesNotExist:
        return

    current_time = get_current_time()
    if key.type in ('Character', 'Account'):
        apicall = APICall.objects.get(type='Character', name='CharacterSheet')
        targets = APIUpdate.objects.filter(apicall=apicall,
                                           apikey=key)
        targets = targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))
        if targets.count() > 0:
            log.info('Queued {0} {1} for capsuler "{2}".'.format(
                    targets.count(),
                    apicall,
                    key.owner
                ))
            for target in targets:
                tasks.append(fetch_charactersheet.s(target.pk))
        else:
            log.info('No character sheets need updating.')
    else:
        apicall = APICall.objects.get(type='Corporation', name='CorporationSheet')
        targets = APIUpdate.objects.filter(apicall=apicall,
                                           apikey=key)
        targets = targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

        if targets.count() > 0:
            log.info('Queued {0} {1} for capsuler "{2}".'.format(
                    targets.count(),
                    apicall,
                    key.owner
                ))
            for target in targets:
                tasks.append(fetch_corporationsheet.s(target.pk))
        else:
            log.info('No corporation sheets need updating')

    if len(tasks) > 0:
        group(tasks).apply_async(queue='transient')

@app.task(name='accounting.update_all_sheets', max_retries=0)
def update_all_sheets(*args, **kwargs):
    tasks = []
    #### Characters
    keys = APIKey.objects.filter(expired=False).exclude(type='Corporation')
    current_time = get_current_time()
    apicall = APICall.objects.get(type='Character', name='CharacterSheet')
    targets = APIUpdate.objects.filter(apicall=apicall,
                                       apikey__in=keys)
    targets = targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

    if targets.count() > 0:
        log.info('Queued {0} {1}'.format(
                targets.count(),
                apicall
            ))
        for target in targets:
            tasks.append(fetch_charactersheet.s(target.pk))
    else:
        log.info('No character sheets need updating.')


    #### Corporations
    corpkeys = APIKey.objects.filter(expired=False, type='Corporation')
    apicall = APICall.objects.get(type='Corporation', name='CorporationSheet')
    targets = APIUpdate.objects.filter(apicall=apicall,
                                       apikey__in=corpkeys)
    targets = targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

    if targets.count() > 0:
        log.info('Queued {0} {1}'.format(
                targets.count(),
                apicall
            ))
        for target in targets:
            tasks.append(fetch_corporationsheet.s(target.pk))
    else:
        log.info('No corporation sheets need updating')

    if len(tasks) > 0:
        group(tasks).apply_async(queue='transient')

@app.task(name='accounting.update_all_apidata', max_retries=0)
def update_all_apidata(*args, **kwargs):
    character_keys = APIKey.objects.filter(expired=False).exclude(type='Corporation')
    corpkeys = APIKey.objects.filter(expired=False, type='Corporation')
    tasks = queue_character_tasks(character_keys) + queue_corporation_tasks(corpkeys)

    if len(tasks) > 0:
        group(tasks).apply_async(queue='transient')

@app.task(name='accounting.update_character_apidata')
def update_character_apidata(character_pk, max_retries=0):
    try:
        character = CharacterSheet.objects.get(pk=character_pk)
    except CharacterSheet.DoesNotExist:
        return
    key_qs = APIKey.objects.filter(pk=character.owner_key.pk)

    tasks = queue_character_tasks(key_qs)
    if len(tasks) > 0:
        group(tasks).apply_async(queue='transient')

@app.task(name='accounting.update_corporation_apidata')
def update_corporation_apidata(corporation_pk, max_retries=0):
    try:
        corporation = CorporationSheet.objects.get(pk=corporation_pk)
    except CorporationSheet.DoesNotExist:
        return
    key_qs = APIKey.objects.filter(pk=corporation.owner_key.pk)
    tasks = queue_corporation_tasks(key_qs)
    if len(tasks) > 0:
        group(tasks).apply_async(queue='transient')


def queue_character_tasks(keys):
    tasks = []

    for name, taskfns in character_tasks.items():
        current_time = get_current_time()
        apicall = APICall.objects.get(type='Character', name=name)
        targets = APIUpdate.objects.filter(apicall=apicall,
                                           apikey__in=keys)
        targets = targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))
        for target in targets:
            log.debug('Queued {0} with keyID {1} with APIUpdate {2}'.format(
                name,
                target.apikey.pk,
                target.pk
            ))

        if targets.count() > 0:
            log.info('Queued {0} {1}'.format(
                targets.count(),
                apicall
            ))
            for fn in taskfns:
                for target in targets:
                    tasks.append(fn.s(target.pk))
        else:
            log.info('No targets for {0} need updating'.format(
                apicall
            ))

    return tasks


def queue_corporation_tasks(corpkeys):
    tasks = []

    for name, taskfns in corporation_tasks.items():
        current_time = get_current_time()
        apicall = APICall.objects.get(type='Corporation', name=name)
        targets = APIUpdate.objects.filter(apicall=apicall,
                                           apikey__in=corpkeys)
        targets = targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

        if targets.count() > 0:
            log.debug('Queued {0} {1}'.format(
                targets.count(),
                apicall
            ))
            for fn in taskfns:
                for target in targets:
                    tasks.append(fn(target.pk))
        else:
            log.info('No targets for {0} need updating'.format(
                apicall
            ))
    return tasks


@app.task(name='accounting.validate_key')
def validate_key(apikey_pk):
    """
    Validates an apikey and register all characters or corporations that should
    be updated using this key.

    The process is roughly:
    1. Check the key against the eveapi. Disable if expired or not existing etc
    2. Create an APIUpdate "target" for the services the access mask grants you
       access to, for every character or corporation the key is valid for.

    :param apikey_pk:
    :return:
    """
    try:
        apikey = APIKey.objects.get(pk=apikey_pk)
    except APIKey.DoesNotExist, dne:
        raise dne
    handler = EveAPIHandler()

    api = handler.get_eveapi()
    auth = api.auth(keyID=apikey.keyID, vCode=apikey.vCode)
    try:
        keyinfo = auth.account.APIKeyInfo()
    except AuthenticationError:
        apikey.brokeness += 1
        if apikey.brokeness == 3:
            apikey.expired = True
        apikey.save()
        APIUpdate.objects.filter(apikey=apikey).delete()
        log.info('APIKey "{0}" owned by "{1}" is disabled according to the eveapi.'.format(
            apikey.name,
            apikey.owner
        ))
        return
    except Exception, ex:
        apikey.brokeness += 1
        if apikey.brokeness == 3:
            apikey.expired = True
        apikey.save()
        APIUpdate.objects.filter(apikey=apikey).delete()
        log.info('Unexpected error while validating APIKey "{0}" owned by "{1}": {2}.'.format(
            apikey.name,
            apikey.owner,
            format_exc(ex)
        ))
        return

    if not keyinfo.key.expires:
        expires = datetime(year=2099, month=1, day=1, tzinfo=UTC)
    else:
        expires = datetime.fromtimestamp(keyinfo.key.expires, tz=UTC)

    if expires < datetime.now(tz=UTC):
        apikey.expired = True
        apikey.save()
        APIUpdate.objects.filter(apikey=apikey).delete()
        return

    apikey.accessMask = keyinfo.key.accessMask
    apikey.type = keyinfo.key.type
    apikey.expires = expires
    apikey.brokeness = 0
    apikey.expired = False

    if keyinfo.key.type == 'Corporation':
        apikey.characterID = keyinfo.key.characters[0].characterID
        apikey.corporationID = keyinfo.key.characters[0].corporationID
        apikey.save()
        targets = []
        # These are all targets for this corporation. Can span several apikeys.
        current_targets = APIUpdate.objects.filter(owner=apikey.corporationID)
        # Remove targets mapped to expired keys, so this key can be set as the
        # target later on.
        current_targets.filter(apikey__expired=True).delete()
        for call_type in APICall.objects.filter(type='Corporation'):
            if call_type.accessMask & apikey.accessMask > 0:
                # We have now found an APICall and an APIKey capable to do that call
                # Check if there's already an APIUpdate that does this call, if not
                # create a target for this key.

                target, created = APIUpdate.objects.update_or_create(owner=apikey.corporationID,
                                                                     apicall=call_type,
                                                                     apikey=apikey)
                # Make sure it's in the list, if not it will be deleted as redundant
                targets.append(target.pk)


        # If a key access mask is changed, there could be residual targets
        # registered with that key, so we'll delete those. They'll be whichever keys
        # are not in targets, as we've gone through all the available APICalls and checked
        # if they have valid targets by this key or any other key.
        APIUpdate.objects.filter(owner=apikey.corporationID, apikey=apikey).exclude(pk__in=targets).delete()

        # Any other keys that provides other accessmasks than this key will then remain.
        # If two keys provide access to the same endpoint for the same entity, whichever
        # key was parsed last, gets the honor. There can be only one!

        # Send a signal if we found a new corporation
        if CorporationSheet.objects.filter(corporationID=apikey.corporationID).count() == 0:
            accounting_new_corporation.send(APIKey,
                                            apikey_pk=apikey.pk,
                                            corporationID=apikey.corporationID)

    elif keyinfo.key.type == 'Character':
        characterID = keyinfo.key.characters[0].characterID
        apikey.characterID = characterID
        if not characterID in apikey.characterIDs:
            apikey.characterIDs = [characterID]
        apikey.save()
        targets = []
        current_targets = APIUpdate.objects.filter(owner=apikey.characterID)
        current_targets.filter(apikey__expired=True).delete()
        for call_type in APICall.objects.filter(type='Character'):
            if call_type.accessMask & apikey.accessMask > 0:
                target, created = APIUpdate.objects.update_or_create(owner=apikey.characterID,
                                                                     apicall=call_type,
                                                                     apikey=apikey)
                # Make sure it's in the list, if not it will be deleted as redundant
                targets.append(target.pk)
        APIUpdate.objects.filter(apikey=apikey, owner=apikey.characterID).exclude(pk__in=targets).delete()
        # In case we have changed which character this apikey points to, we remove the matching
        # character sheet.
        CharacterSheet.objects.filter(owner_key=apikey).exclude(pk=apikey.characterID).delete()

        if CharacterSheet.objects.filter(characterID=apikey.characterID).count() == 0:
            accounting_new_character.send(APIKey,
                                          apikey_pk=apikey.pk,
                                          characterID=apikey.characterID)
    elif keyinfo.key.type == 'Account':
        apikey.save()
        targets = []
        characterIDs = []
        for char in keyinfo.key.characters:
            characterIDs.append(char.characterID)
            current_targets = APIUpdate.objects.filter(owner=char.characterID)
            current_targets.filter(apikey__expired=True).delete()
            for call_type in APICall.objects.filter(type='Character'):
                if call_type.accessMask & apikey.accessMask > 0:
                    target, created = APIUpdate.objects.update_or_create(owner=char.characterID,
                                                                         apicall=call_type,
                                                                         apikey=apikey)
                    targets.append(target.pk)
            if CharacterSheet.objects.filter(characterID=char.characterID).count() == 0:
                accounting_new_character.send(APIKey,
                                              apikey_pk=apikey.pk,
                                              characterID=char.characterID)
        apikey.characterIDs = characterIDs
        apikey.save()

        APIUpdate.objects.filter(apikey=apikey).exclude(pk__in=targets).delete()
        # If this account key previously had characters associated to it that has been biomassed,
        # we delete them.
        CharacterSheet.objects.filter(owner_key=apikey).exclude(pk__in=characterIDs).delete()
    else:
        apikey.save()