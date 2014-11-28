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
from stationspinner.universe.models import APICall
from stationspinner.character.tasks import API_MAP as character_tasks, fetch_charactersheet
from stationspinner.corporation.tasks import API_MAP as corporation_tasks, fetch_corporationsheet

from celery.utils.log import get_task_logger

log = get_task_logger(__name__)

@app.task(name='accounting.update_capsulers')
def update_capsulers():
    chain(update_capsuler_keys.s(), update_all_sheets.s(), update_all_apidata.s())()

@app.task(name='accounting.update_capsuler_keys')
def update_capsuler_keys(*args, **kwargs):
    capsulers = Capsuler.objects.filter(is_active=True)

    active_keys = APIKey.objects.filter(expired=False, owner__in=capsulers)
    log.info('Validating {0} keys'.format(active_keys.count()))
    validate_key.map([key.pk for key in active_keys]).apply_async()


def queue_capsuler_keys(capsuler):
    log.info('Refreshing capsuler "{0}" keys'.format(capsuler.username))

    keys = APIKey.objects.filter(owner=capsuler)
    if keys.count() == 0:
        return None

    return validate_key.map([apikey.pk for apikey in keys])

@app.task(name='accounting.update_all_sheets')
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
        tasks.append(fetch_charactersheet.map([t.pk for t in targets]))
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
        tasks.append(fetch_corporationsheet.map([t.pk for t in targets]))
    else:
        log.info('No corporation sheets need updating')

    group(tasks).apply_async()

@app.task(name='accounting.update_all_apidata')
def update_all_apidata(*args, **kwargs):
    group(queue_character_tasks() + queue_corporation_tasks()).apply_async()

def queue_character_tasks():
    keys = APIKey.objects.filter(expired=False).exclude(type='Corporation')
    tasks = []

    for name, taskfns in character_tasks.items():
        current_time = get_current_time()
        apicall = APICall.objects.get(type='Character', name=name)
        targets = APIUpdate.objects.filter(apicall=apicall,
                                           apikey__in=keys)
        targets = targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

        if targets.count() > 0:
            log.info('Queued {0} {1}'.format(
                targets.count(),
                apicall
            ))
            for fn in taskfns:
                tasks.append(fn.map([t.pk for t in targets]))
        else:
            log.info('No targets for {0} need updating'.format(
                apicall
            ))

    return tasks


def queue_corporation_tasks():
    corpkeys = APIKey.objects.filter(expired=False, type='Corporation')
    tasks = []

    for name, taskfns in corporation_tasks.items():
        current_time = get_current_time()
        apicall = APICall.objects.get(type='Corporation', name=name)
        targets = APIUpdate.objects.filter(apicall=apicall,
                                           apikey__in=corpkeys)
        targets = targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

        if targets.count() > 0:
            log.info('Queued {0} {1}'.format(
                targets.count(),
                apicall
            ))
            for fn in taskfns:
                tasks.append(fn.map([t.pk for t in targets]))
        else:
            log.info('No targets for {0} need updating'.format(
                apicall
            ))
    return tasks


@app.task(name='accounting.validate_key')
def validate_key(apikey_pk):
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
        apikey.expired = True
        apikey.save()
        log.info('APIKey "{0}" owned by "{1}" is disabled according to the eveapi.'.format(
            apikey.name,
            apikey.owner
        ))
        return
    except Exception, ex:
        apikey.expired = True
        apikey.save()
        log.info('Unexpected error while validating APIKey "{0}" owned by "{1}": {2}.'.format(
            apikey.name,
            apikey.owner,
            format_exc(ex)
        ))
        return

    if not keyinfo.key.expires:
        expires = datetime.fromtimestamp(2000000000, tz=UTC)
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

    if keyinfo.key.type == 'Corporation':
        apikey.characterID = keyinfo.key.characters[0].characterID
        apikey.corporationID = keyinfo.key.characters[0].corporationID
        apikey.save()
        for call_type in APICall.objects.all():
            if call_type.accessMask & apikey.accessMask > 0:
                APIUpdate.objects.update_or_create(owner=apikey.corporationID,
                                                   apicall=call_type,
                                                   apikey=apikey)

    elif keyinfo.key.type == 'Character':
        apikey.characterID = keyinfo.key.characters[0].characterID
        apikey.save()
        for call_type in APICall.objects.all():
            if call_type.accessMask & apikey.accessMask > 0:
                APIUpdate.objects.update_or_create(owner=apikey.characterID,
                                                   apicall=call_type,
                                                   apikey=apikey)
    elif keyinfo.key.type == 'Account':
        apikey.save()

        for char in keyinfo.key.characters:
            for call_type in APICall.objects.all():
                if call_type.accessMask & apikey.accessMask > 0:
                    APIUpdate.objects.update_or_create(owner=char.characterID,
                                                       apicall=call_type,
                                                       apikey=apikey)
    else:
        apikey.save()