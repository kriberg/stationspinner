from stationspinner.celery import app
from stationspinner.accounting.models import APIKey
from stationspinner.character.models import CharacterSheet, WalletJournal, \
    Blueprint, Contact, Research, AssetList, MarketOrder, Medal, Notification, \
    WalletTransaction, PlanetaryColony, Contract, ContractItem, ContractBid, \
    SkillQueue, MailingList, ContactNotification, MailMessage, \
    SkillInTraining, IndustryJob, IndustryJobHistory, NPCStanding, Asset

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
def fetch_blueprints(character_pk):
    try:
        character = CharacterSheet.objects.get(pk=character_pk)
    except CharacterSheet.DoesNotExist, dbe:
        log.error('Requested characterID {0} could not be fetched.'.format(character_pk))
        raise dbe

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(character.owner_key)

    blueprintsData = auth.char.Blueprints(characterID=character_pk)

    blueprintsIDs = handler.autoparseList(blueprintsData.blueprints,
                          Blueprint,
                          unique_together=('itemID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)

    deleted_blueprints = Blueprint.objects.filter(owner=character) \
        .exclude(pk__in=blueprintsIDs).delete()


@app.task(name='character.fetch_contacts')
def fetch_contacts(character_pk):
    try:
        character = CharacterSheet.objects.get(pk=character_pk)
    except CharacterSheet.DoesNotExist, dbe:
        log.error('Requested characterID {0} could not be fetched.'.format(character_pk))
        raise dbe

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(character.owner_key)

    api_data = auth.char.ContactList(characterID=character_pk)

    cIDs = handler.autoparseList(api_data.contactList,
                          Contact,
                          unique_together=('contactID',),
                          extra_selectors={'owner': character,
                                           'listType': 'Private'},
                          owner=character,
                          pre_save=True)
    cIDs.extend(handler.autoparseList(api_data.corporateContactList,
                          Contact,
                          unique_together=('contactID',),
                          extra_selectors={'owner': character,
                                           'listType': 'Corporate'},
                          owner=character,
                          pre_save=True))
    cIDs.extend(handler.autoparseList(api_data.allianceContactList,
                          Contact,
                          unique_together=('contactID',),
                          extra_selectors={'owner': character,
                                           'listType': 'Alliance'},
                          owner=character,
                          pre_save=True))

    Contact.objects.filter(owner=character).exclude(pk__in=cIDs).delete()

@app.task(name='character.fetch_research')
def fetch_research(character_pk):
    try:
        character = CharacterSheet.objects.get(pk=character_pk)
    except CharacterSheet.DoesNotExist, dbe:
        log.error('Requested characterID {0} could not be fetched.'.format(character_pk))
        raise dbe

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(character.owner_key)

    api_data = auth.char.Research(characterID=character_pk)

    rIDs = handler.autoparseList(api_data.research,
                          Research,
                          unique_together=('agentID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)
    Research.objects.filter(owner=character).exclude(pk__in=rIDs).delete()


@app.task(name='character.fetch_marketorders')
def fetch_marketorders(character_pk):
    try:
        character = CharacterSheet.objects.get(pk=character_pk)
    except CharacterSheet.DoesNotExist, dbe:
        log.error('Requested characterID {0} could not be fetched.'.format(character_pk))
        raise dbe

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(character.owner_key)

    api_data = auth.char.MarketOrders(characterID=character_pk)

    handler.autoparseList(api_data.orders,
                          MarketOrder,
                          unique_together=('orderID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)

@app.task(name='character.fetch_medals')
def fetch_medals(character_pk):
    try:
        character = CharacterSheet.objects.get(pk=character_pk)
    except CharacterSheet.DoesNotExist, dbe:
        log.error('Requested characterID {0} could not be fetched.'.format(character_pk))
        raise dbe

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(character.owner_key)

    api_data = auth.char.Medals(characterID=character_pk)

    mIDs = handler.autoparseList(api_data.currentCorporation,
                          Medal,
                          unique_together=('medalID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)
    mIDs.extend(handler.autoparseList(api_data.otherCorporations,
                          Medal,
                          unique_together=('medalID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True))

    Medal.objects.filter(owner=character).exclude(pk__in=mIDs).delete()


@app.task(name='character.fetch_assetlist')
def fetch_assetlist(character_pk):
    try:
        character = CharacterSheet.objects.get(pk=character_pk)
    except CharacterSheet.DoesNotExist, dbe:
        log.error('Requested characterID {0} could not be fetched.'.format(character_pk))
        raise dbe

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(character.owner_key)

    api_data = auth.char.AssetList(characterID=character_pk)

    assetlist = AssetList(owner=character,
                          retrieved=api_data._meta.currentTime)

    assetlist.items = handler.asset_parser(api_data.assets,
                                           Asset,
                                           character)
    assetlist.save()


@app.task(name='character.fetch_walletjournal')
def fetch_walletjournal(character_pk):
    try:
        character = CharacterSheet.objects.get(pk=character_pk)
    except CharacterSheet.DoesNotExist, dbe:
        log.error('Requested characterID {0} could not be fetched.'.format(character_pk))
        raise dbe

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(character.owner_key)

    api_data = auth.char.WalletJournal(characterID=character_pk)

    handler.autoparseList(api_data.orders,
                          WalletJournal,
                          unique_together=('orderID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)

@app.task(name='character.fetch_skillqueue')
def fetch_skillqueue(character_pk):
    try:
        character = CharacterSheet.objects.get(pk=character_pk)
    except CharacterSheet.DoesNotExist, dbe:
        log.error('Requested characterID {0} could not be fetched.'.format(character_pk))
        raise dbe

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(character.owner_key)

    api_data = auth.char.SkillQueue(characterID=character_pk)

    handler.autoparseList(api_data.skillqueue,
                          SkillQueue,
                          owner=character,
                          pre_delete=True,
                          pre_save=True)

@app.task(name='character.fetch_skill_in_training')
def fetch_skill_in_training(character_pk):
    try:
        character = CharacterSheet.objects.get(pk=character_pk)
    except CharacterSheet.DoesNotExist, dbe:
        log.error('Requested characterID {0} could not be fetched.'.format(character_pk))
        raise dbe

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(character.owner_key)

    api_data = auth.char.SkillInTraining(characterID=character_pk)

    obj = handler.autoparseObj(api_data,
                         SkillInTraining,
                         extra_selectors={'owner': character},
                         owner=character,
                         exclude=('currentTQTime',))
    obj.currentTQTime = api_data.currentTQTime.data
    obj.save()