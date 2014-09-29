from stationspinner.celery import app
from stationspinner.accounting.models import APIKey
from stationspinner.character.models import CharacterSheet, \
    Blueprint
from stationspinner.libs.eveapihandler import EveAPIHandler


from celery.utils.log import get_task_logger

log = get_task_logger(__name__)

@app.task(name='character.fetch_charactersheet')
def fetch_charactersheet(character_pk, apikey_pk):
    try:
        apikey = APIKey.objects.get(pk=apikey_pk)
    except APIKey.DoesNotExist, dne:
        log.error('APIKey {0} was deleted mid-flight.'.format(apikey_pk))
        raise dne



    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(apikey)
    sheet = auth.char.CharacterSheet(characterID=character_pk)

    try:
        character = CharacterSheet.objects.get(characterID=sheet.characterID)

        # As long as the apikey can get a valid character sheet back from the
        # eveapi, we'll allow the CS model to change owner and/or key
        if character.owner_key != apikey:
            log.warning('Character {0} "{1}" changed APIKey to keyID={2}.'.format(sheet.characterID,
                                                                                  sheet.name,
                                                                                  apikey.keyID))
        if character.owner != apikey.owner:
            log.warning('Character {0} "{1}" changed owner from "{2}" to "{3}".'.format(sheet.characterID,
                                                                                  sheet.name,
                                                                                  character.owner,
                                                                                  apikey.owner))
    except CharacterSheet.DoesNotExist:
        character = CharacterSheet(characterID=sheet.characterID)
    except Exception, ex:
        log.warning('Character {0} "{1}" could not be updated with APIKey {2}.'.format(sheet.characterID,
                                                                                       sheet.name,
                                                                                       apikey.keyID))
        raise ex

    character.owner_key = apikey
    character.owner = apikey.owner
    character.update_from_api(sheet, handler)

    log.info('Character {0} "{1}" updated.'.format(sheet.characterID,
                                                      sheet.name))
    return character.pk

@app.task(name='character.fetch_blueprints')
def fetch_blueprints(character_pk, apikey_pk):
    try:
        apikey = APIKey.objects.get(pk=apikey_pk)
    except APIKey.DoesNotExist, dne:
        log.error('APIKey {0} was deleted mid-flight.'.format(apikey_pk))
        raise dne

    try:
        character = CharacterSheet.objects.get(pk=character_pk, owner_key=apikey)
    except CharacterSheet.DoesNotExist, dbe:
        log.warning('CharacterID {0} could not be fetched with APIKey {1}.'.format(character_pk, apikey_pk))
        raise dbe

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(apikey)

    blueprintsData = auth.char.Blueprints(characterID=character_pk)

    blueprintsIDs = handler.autoparseList(blueprintsData.blueprints,
                          Blueprint,
                          unique_together=('itemID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)

    deleted_blueprints = Blueprint.objects.filter(owner=character) \
        .exclude(pk__in=blueprintsIDs).delete()
