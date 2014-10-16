from stationspinner.celery import app
from celery import group
from datetime import datetime

from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.accounting.models import Capsuler, APIKey
from stationspinner.character.tasks import fetch_charactersheet, \
    fetch_blueprints, \
    fetch_assetlist, \
    fetch_contacts, \
    fetch_marketorders, \
    fetch_medals, \
    fetch_research, \
    fetch_skillqueue, \
    fetch_skill_in_training

from stationspinner.corporation.tasks import fetch_corporationsheet, \
    fetch_assetlist as corp_fetch_assetlist, \
    fetch_membertracking as corp_fetch_membertracking

from celery.utils.log import get_task_logger

log = get_task_logger(__name__)

def refresh_capsuler(capsuler_pk):
    start = datetime.now()
    try:
        capsuler = Capsuler.objects.get(pk=capsuler_pk)
        log.info('Refreshing capsuler "{0}"'.format(capsuler.username))
    except Capsuler.DoesNotExist:
        log.error('Tried to refresh non-existant capsuler, pk={0}'.format(capsuler_pk))
        return None

    keys = APIKey.objects.filter(owner=capsuler)
    if keys.count() == 0:
        return None

    validation = validate_key.map([apikey.pk for apikey in keys])
    tasks = validation.apply_async()
    valid_characters = tasks.get()
    log.debug('Valid characterIDs: {0}'.format(valid_characters))

    # Since we have a bunch of keys, some characters could be available on several of them.
    # We'll use the key with the biggest access mask, in such cases.
    masks = {}
    for key in keys:
        masks[key.pk] = key.accessMask
    chars_to_keys = {}


    for charlists in valid_characters:
        # Corp keys have no valid chars, so we'll skip those
        if not charlists:
            continue
        for char_id, key_pk  in charlists:
            if not char_id in chars_to_keys:
                chars_to_keys[char_id] = key_pk
            else:
                current = masks[chars_to_keys[char_id]]
                new = masks[key_pk]
                if new > current:
                    chars_to_keys[char_id] = key_pk

    update_characters = fetch_charactersheet.starmap(chars_to_keys.items())
    tasks = update_characters.apply_async()

    characterIDs = tasks.get()

    corpkeys = keys.filter(type='Corporation', expired=False)
    corp_to_keys = {}
    for key in corpkeys:
        if not key.corporationID in corp_to_keys:
            corp_to_keys[key.corporationID] = key.pk
        else:
            current = masks[corpkeys[key.corporationID]]
            new = masks[key.pk]
            if new > current:
                corp_to_keys[key.corporationID] = key.pk

    updated_corporations = fetch_corporationsheet.starmap(corp_to_keys.items())
    tasks = updated_corporations.apply_async()

    corpIDs = tasks.get()

    jobs = group(fetch_blueprints.map(characterIDs),
                  fetch_assetlist.map(characterIDs),
                  fetch_contacts.map(characterIDs),
                  fetch_marketorders.map(characterIDs),
                  fetch_medals.map(characterIDs),
                  fetch_research.map(characterIDs),
                  fetch_skillqueue.map(characterIDs),
                  fetch_skill_in_training.map(characterIDs),
                  corp_fetch_assetlist.map(corpIDs),
                  corp_fetch_membertracking.map(corpIDs))()

    result = jobs.get()
    log.info('Capsuler {0} updated in {1} seconds.'.format(capsuler, (datetime.now()-start).total_seconds()))
    return result


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
        return None
    apikey.accessMask = keyinfo.key.accessMask
    apikey.type = keyinfo.key.type
    if keyinfo.key.type == 'Corporation':
        apikey.characterID = keyinfo.key.characters[0].characterID
        apikey.corporationID = keyinfo.key.characters[0].corporationID
        apikey.save()
        return

    character_ids = [(char.characterID, apikey_pk) for char in keyinfo.key.characters]
    apikey.save()

    return character_ids


#TODO: task to disable expired keys and disable characters/corporations