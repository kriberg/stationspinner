from stationspinner.celery import app
from celery import group, chain
from datetime import datetime

from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.accounting.models import Capsuler, APIKey
from stationspinner.character.tasks import fetch_charactersheet, \
    fetch_blueprints

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

    keys = APIKey.objects.filter(owner=capsuler_pk)
    if keys.count() == 0:
        return None

    validation = group(validate_key.s(apikey.pk) for apikey in keys)
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
        for char_id, key_pk  in charlists:
            if not char_id in chars_to_keys:
                chars_to_keys[char_id] = key_pk
            else:
                current = masks[chars_to_keys[char_id]]
                new = masks[key_pk]
                if new.accessMask > current.accessMask:
                    chars_to_keys[char_id] = key_pk

    update_sheets = group(fetch_charactersheet.s(character_pk, apikey_pk) \
                          for character_pk, apikey_pk in chars_to_keys.items())

    tasks = update_sheets.apply_async()
    characterIDs = tasks.get()

    update_blueprints = group(fetch_blueprints.s(character_pk, apikey_pk) \
                          for character_pk, apikey_pk in chars_to_keys.items())

    tasks = update_blueprints.apply_async()
    tasks.get()
    log.info('Capsuler {0} updated in {1} seconds.'.format(capsuler, (datetime.now()-start).total_seconds()))


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
    character_ids = [(char.characterID, apikey_pk) for char in keyinfo.key.characters]

    return character_ids


#TODO: task to disable expired keys and disable characters/corporations