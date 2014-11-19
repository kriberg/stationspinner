from stationspinner.celery import app
from celery import group, chord, chain
from datetime import datetime
from django.db.models import Q

from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.accounting.models import Capsuler, APIKey, APIUpdate
from stationspinner.libs.pragma import get_current_time
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
    for capsuler in capsulers:
        queue_capsuler_keys(capsuler).apply_async()

    log.info('Queued updating of all capsulers.')


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
    targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

    if targets.count() > 0:
        tasks.append(fetch_charactersheet.map([t.pk for t in targets]))


    #### Corporations
    corpkeys = APIKey.objects.filter(expired=False, type='Corporation')
    apicall = APICall.objects.get(type='Corporation', name='CorporationSheet')
    targets = APIUpdate.objects.filter(apicall=apicall,
                                       apikey__in=corpkeys)
    targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

    if targets.count() > 0:
        tasks.append(fetch_corporationsheet.map([t.pk for t in targets]))

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
        targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

        if targets.count() > 0:
            for fn in taskfns:
                tasks.append(fn.map([t.pk for t in targets]))

    return tasks


def queue_corporation_tasks():
    corpkeys = APIKey.objects.filter(expired=False, type='Corporation')
    tasks = []

    for name, taskfns in corporation_tasks.items():
        current_time = get_current_time()
        apicall = APICall.objects.get(type='Corporation', name=name)
        targets = APIUpdate.objects.filter(apicall=apicall,
                                           apikey__in=corpkeys)
        targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

        if targets.count() > 0:
            for fn in taskfns:
                tasks.append(fn.map([t.pk for t in targets]))
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
    keyinfo = auth.account.APIKeyInfo()

    expires = datetime.fromtimestamp(keyinfo.key.expires)
    if expires < datetime.now():
        apikey.expired = True
        APIUpdate.objects.filter(apikey=apikey).delete()
        return

    apikey.accessMask = keyinfo.key.accessMask
    apikey.type = keyinfo.key.type

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
        pass