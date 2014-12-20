from stationspinner.celery import app
from stationspinner.accounting.models import APIKey, APIUpdate
from stationspinner.character.models import CharacterSheet, WalletJournal, \
    Blueprint, Contact, Research, AssetList, MarketOrder, Medal, Notification, \
    WalletTransaction, PlanetaryColony, Contract, ContractItem, ContractBid, \
    SkillQueue, MailingList, ContactNotification, MailMessage, \
    SkillInTraining, IndustryJob, IndustryJobHistory, NPCStanding, Asset

from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.libs.eveapi.eveapi import AuthenticationError

from celery.utils.log import get_task_logger

log = get_task_logger(__name__)

def _get_character_auth(apiupdate_pk):
    try:
        target = APIUpdate.objects.get(pk=apiupdate_pk)
    except APIUpdate.DoesNotExist, dne:
        log.error('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        raise dne

    character = CharacterSheet.objects.get(pk=target.owner)

    return target, character


@app.task(name='character.fetch_charactersheet')
def fetch_charactersheet(apiupdate_pk):
    try:
        target = APIUpdate.objects.get(pk=apiupdate_pk)
    except APIUpdate.DoesNotExist, dne:
        log.error('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        raise dne
    apikey = target.apikey

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(apikey)
    try:
        sheet = auth.char.CharacterSheet(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

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
        log.warning('Character {0} "{1}" could not be updated with APIKey {2} ({3}).'.format(sheet.characterID,
                                                                                       sheet.name,
                                                                                       apikey.keyID,
                                                                                       apikey.pk))
        raise ex

    character.owner_key = apikey
    character.owner = apikey.owner
    character.update_from_api(sheet, handler)

    target.updated(sheet)

    log.info('Character {0} "{1}" updated.'.format(sheet.characterID,
                                                      sheet.name))
    return character.pk


@app.task(name='character.fetch_blueprints')
def fetch_blueprints(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()

    auth = handler.get_authed_eveapi(target.apikey)

    try:
        api_data = auth.char.Blueprints(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    blueprintsIDs = handler.autoparseList(api_data.blueprints,
                          Blueprint,
                          unique_together=('itemID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)

    Blueprint.objects.filter(owner=character) \
        .exclude(pk__in=blueprintsIDs).delete()
    target.updated(api_data)


@app.task(name='character.fetch_contacts')
def fetch_contacts(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)

    try:
        api_data = auth.char.ContactList(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

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
    target.updated(api_data)


@app.task(name='character.fetch_research')
def fetch_research(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.char.Research(characterID=target.owner)
    except AuthenticationError:
            log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
                target.apikey.keyID,
                target.apikey.owner
            ))
            target.delete()
            return
    rIDs = handler.autoparseList(api_data.research,
                          Research,
                          unique_together=('agentID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)
    Research.objects.filter(owner=character).exclude(pk__in=rIDs).delete()
    target.updated(api_data)


@app.task(name='character.fetch_marketorders')
def fetch_marketorders(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.char.MarketOrders(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    handler.autoparseList(api_data.orders,
                          MarketOrder,
                          unique_together=('orderID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)
    target.updated(api_data)


@app.task(name='character.fetch_medals')
def fetch_medals(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()

    auth = handler.get_authed_eveapi(target.apikey)

    try:
        api_data = auth.char.Medals(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

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
    target.updated(api_data)


@app.task(name='character.fetch_assetlist')
def fetch_assetlist(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)

    try:
        api_data = auth.char.AssetList(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return


    assetlist = AssetList(owner=character,
                          retrieved=api_data._meta.currentTime)

    assetlist.items = handler.asset_parser(api_data.assets,
                                           Asset,
                                           character)
    assetlist.save()
    target.updated(api_data)


@app.task(name='character.fetch_walletjournal')
def fetch_walletjournal(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.char.WalletJournal(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return
    handler.autoparseList(api_data.transactions,
                          WalletJournal,
                          unique_together=('refID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)
    target.updated(api_data)


@app.task(name='character.fetch_skillqueue')
def fetch_skillqueue(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.char.SkillQueue(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return
    handler.autoparseList(api_data.skillqueue,
                          SkillQueue,
                          owner=character,
                          pre_delete=True,
                          pre_save=True)
    target.updated(api_data)


@app.task(name='character.fetch_skill_in_training')
def fetch_skill_in_training(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.char.SkillInTraining(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return
    obj = handler.autoparseObj(api_data,
                         SkillInTraining,
                         extra_selectors={'owner': character},
                         owner=character,
                         exclude=('currentTQTime',))
    obj.currentTQTime = api_data.currentTQTime.data
    obj.save()
    target.updated(api_data)




API_MAP = {
        'ContactList': (fetch_contacts,),
        'Research': (fetch_research,),
        'MarketOrders': (fetch_marketorders,),
        'Medals': (fetch_medals,),
        'AssetList': (fetch_assetlist, fetch_blueprints),
        'WalletJournal': (fetch_walletjournal,),
        'SkillQueue': (fetch_skillqueue,),
        'SkillInTraining': (fetch_skill_in_training,),
    }