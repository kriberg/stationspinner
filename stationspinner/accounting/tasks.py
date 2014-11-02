from stationspinner.celery import app
from celery import group
from datetime import datetime
from django.db.models import Q

from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.accounting.models import Capsuler, APIKey, APIUpdate
from stationspinner.libs.pragma import get_current_time
from stationspinner.universe.models import APICall
from stationspinner.character.tasks import API_MAP as character_tasks
from stationspinner.corporation.tasks import API_MAP as corporation_tasks

from celery.utils.log import get_task_logger

log = get_task_logger(__name__)

def update_capsuler(capsuler_pk):
    try:
        capsuler = Capsuler.objects.get(pk=capsuler_pk)
        log.info('Refreshing capsuler "{0}"'.format(capsuler.username))
    except Capsuler.DoesNotExist:
        log.error('Tried to refresh non-existant capsuler, pk={0}'.format(capsuler_pk))
        return None
    start = datetime.now()

    keys = APIKey.objects.filter(owner=capsuler)
    if keys.count() == 0:
        return None

    tasks = validate_key.map([apikey.pk for apikey in keys]).apply_async()
    tasks.get()

    keys = APIKey.objects.filter(owner=capsuler, expired=False).exclude(type='Corporation')

    for task_batch in character_tasks:
        batch = []
        for name, taskfns in task_batch.items():
            current_time = get_current_time()
            apicall = APICall.objects.get(type='Character', name=name)
            targets = APIUpdate.objects.filter(apicall=apicall,
                                               apikey__in=keys)
            targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

            if targets.count() > 0:
                for fn in taskfns:
                    batch.append(fn.map([t.pk for t in targets]))
        tasks = group(batch).apply_async()
        tasks.get()

    corpkeys = APIKey.objects.filter(owner=capsuler, expired=False, type='Corporation')
    for task_batch in corporation_tasks:
        batch = []
        for name, taskfns in task_batch.items():
            current_time = get_current_time()
            apicall = APICall.objects.get(type='Corporation', name=name)
            targets = APIUpdate.objects.filter(apicall=apicall,
                                               apikey__in=corpkeys)
            targets.filter(Q(cached_until__lte=current_time) | Q(cached_until=None))

            if targets.count() > 0:
                for fn in taskfns:
                    batch.append(fn.map([t.pk for t in targets]))
        tasks = group(batch).apply_async()
        tasks.get()

    log.info('Capsuler "{0}" updated in {1} seconds.'.format(capsuler, (datetime.now()-start).total_seconds()))


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