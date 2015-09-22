from stationspinner.celery import app
from stationspinner.accounting.models import APIKey, APIUpdate
from stationspinner.character.models import CharacterSheet, WalletJournal, \
    Blueprint, Contact, Research, AssetList, MarketOrder, Medal, Notification, \
    WalletTransaction, PlanetaryColony, Contract, ContractItem, ContractBid, \
    SkillQueue, MailingList, ContactNotification, MailMessage, \
    SkillInTraining, IndustryJob, IndustryJobHistory, NPCStanding, Asset, \
    ItemLocationName
from stationspinner.universe.models import EveName
from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.libs.eveapi.eveapi import AuthenticationError
from stationspinner.libs.assethandlers import CharacterAssetHandler
from traceback import format_exc

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

def _blocker(itr, size):
    for i in xrange(0, len(itr), size):
        yield itr[i:i+size]

@app.task(name='character.fetch_charactersheet', max_retries=0)
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


@app.task(name='character.fetch_blueprints', max_retries=0)
def fetch_blueprints(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
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

    blueprintsIDs = handler.autoparse_list(api_data.blueprints,
                          Blueprint,
                          unique_together=('itemID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)

    Blueprint.objects.filter(owner=character) \
        .exclude(pk__in=blueprintsIDs).delete()
    target.updated(api_data)


@app.task(name='character.fetch_contacts', max_retries=0)
def fetch_contacts(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
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

    cIDs = handler.autoparse_list(api_data.contactList,
                          Contact,
                          unique_together=('contactID',),
                          extra_selectors={'owner': character,
                                           'listType': 'Private'},
                          owner=character,
                          pre_save=True)
    cIDs.extend(handler.autoparse_list(api_data.corporateContactList,
                          Contact,
                          unique_together=('contactID',),
                          extra_selectors={'owner': character,
                                           'listType': 'Corporate'},
                          owner=character,
                          pre_save=True))
    cIDs.extend(handler.autoparse_list(api_data.allianceContactList,
                          Contact,
                          unique_together=('contactID',),
                          extra_selectors={'owner': character,
                                           'listType': 'Alliance'},
                          owner=character,
                          pre_save=True))

    Contact.objects.filter(owner=character).exclude(pk__in=cIDs).delete()
    target.updated(api_data)


@app.task(name='character.fetch_research', max_retries=0)
def fetch_research(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
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
    rIDs = handler.autoparse_list(api_data.research,
                          Research,
                          unique_together=('agentID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)
    Research.objects.filter(owner=character).exclude(pk__in=rIDs).delete()
    target.updated(api_data)


@app.task(name='character.fetch_marketorders', max_retries=0)
def fetch_marketorders(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
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

    handler.autoparse_list(api_data.orders,
                          MarketOrder,
                          unique_together=('orderID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)
    target.updated(api_data)


@app.task(name='character.fetch_medals', max_retries=0)
def fetch_medals(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
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

    mIDs = handler.autoparse_list(api_data.currentCorporation,
                          Medal,
                          unique_together=('medalID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)
    mIDs.extend(handler.autoparse_list(api_data.otherCorporations,
                          Medal,
                          unique_together=('medalID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True))

    Medal.objects.filter(owner=character).exclude(pk__in=mIDs).delete()
    target.updated(api_data)


@app.task(name='character.fetch_assetlist', max_retries=0)
def fetch_assetlist(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
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

    assetlist.items, itemIDs_with_names = handler.asset_parser(api_data.assets,
                                                               Asset,
                                                               character,
                                                               target)
    assetlist.save()
    names_registered = 0
    log.debug('Fetching the item name of {0} items.'.format(len(itemIDs_with_names)))

    for block in _blocker(itemIDs_with_names, 1000):
        try:
            if target.apikey.type == 'Account':

                api_data = auth.char.Locations(characterID=character.pk,
                                               IDs=','.join(block))
            else:
                api_data = auth.char.Locations(IDs=','.join(block))
        except Exception, ex:
            log.warning('Could not fetch names for itemIDs "{0}", with APIKey {1}.\n{2}'.format(
                block,
                target.apikey.pk,
                format_exc(ex)
            ))
            continue
        IDs = handler.autoparse_list(api_data.locations,
                               ItemLocationName,
                               unique_together=('itemID',),
                               extra_selectors={'owner': character},
                               owner=character,
                               pre_save=True)
        names_registered += len(IDs)
    old_names = ItemLocationName.objects.filter(owner=character).exclude(pk__in=itemIDs_with_names)
    log.debug('Fetched {0} names and deleted {1} for "{2}"'.format(
        names_registered,
        old_names.count(),
        character
    ))
    old_names.delete()

    for asset in Asset.objects.filter(owner=character):
        asset.update_search_tokens()

    handler = CharacterAssetHandler()
    handler.invalidate_entity(character.pk)
    target.updated(api_data)


@app.task(name='character.fetch_walletjournal', max_retries=0)
def fetch_walletjournal(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
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
    handler.autoparse_list(api_data.transactions,
                          WalletJournal,
                          unique_together=('refID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)
    target.updated(api_data)


@app.task(name='character.fetch_wallettransactions', max_retries=0)
def fetch_wallettransactions(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.char.WalletTransactions(characterID=target.owner, rowCount=2560)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return
    handler.autoparse_list(api_data.transactions,
                          WalletTransaction,
                          unique_together=('transactionID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          exclude=['transactionType', 'transactionFor'],
                          pre_save=True)
    target.updated(api_data)


@app.task(name='character.fetch_skillqueue', max_retries=0)
def fetch_skillqueue(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
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
    skills = handler.autoparse_list(api_data.skillqueue,
                                    SkillQueue,
                                    unique_together=('typeID', 'level'),
                                    extra_selectors={'owner': character},
                                    owner=character,
                                    pre_save=True)
    SkillQueue.objects.filter(owner=character).exclude(pk__in=skills).delete()
    target.updated(api_data)


@app.task(name='character.fetch_skill_in_training', max_retries=0)
def fetch_skill_in_training(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
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


@app.task(name='character.fetch_notifications', max_retries=0)
def fetch_notifications(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.char.Notifications(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    notifications = handler.autoparse_list(api_data.notifications,
                          Notification,
                          unique_together=('notificationID',),
                          extra_selectors={'owner': character},
                          owner=character,
                          pre_save=True)

    unfetched_notifications = Notification.objects.filter(
        owner=character,
        pk__in=notifications,
        broken=False,
        raw_message=None)


    if unfetched_notifications.count() > 0:
        note_texts = auth.char.NotificationTexts(characterID=target.owner,
                                               IDs=[note.notificationID for note in unfetched_notifications])

        for note_data in note_texts.notifications:
            try:
                note = Notification.objects.get(notificationID=note_data.notificationID,
                                                owner=target.owner)
                note.raw_message = note_data.data
                note.save()
            except Notification.DoesNotExist:
                log.error('Could not fetch notification text for notificationID {0} belonging to character "{1}".'.format(
                    note_data.notificationID,
                    character
                ))
            #except:
            #    note.broken = True
            #    note.save()


    target.updated(api_data)


@app.task(name='character.fetch_mails', max_retries=0)
def fetch_mails(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.char.MailMessages(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    mails = handler.autoparse_shared_list(api_data.messages,
                          MailMessage,
                          ('messageID',),
                          character,
                          pre_save=True)

    unfetched_mails = MailMessage.objects.filter(
        owners__in=[character.pk],
        pk__in=mails,
        broken=False,
        raw_message=None)


    EveName.objects.populate()
    if unfetched_mails.count() > 0:
        mail_bodies = auth.char.MailBodies(characterID=target.owner,
                                               IDs=[mail.messageID for mail in unfetched_mails])

        for mail_body in mail_bodies.messages:
            try:
                mail = MailMessage.objects.get(messageID=mail_body.messageID)
                mail.raw_message = mail_body.data
                mail.populate_receivers()
                mail.save()
            except MailMessage.DoesNotExist:
                log.error('Could not fetch message body for messageID {0} belonging to character "{1}".'.format(
                    mail_body.messageID,
                    character
                ))
            #except:
            #    note.broken = True
            #    note.save()




    target.updated(api_data)


@app.task(name='character.fetch_mailinglists', max_retries=0)
def fetch_mailinglists(apiupdate_pk):
    try:
        target, character = _get_character_auth(apiupdate_pk)
    except CharacterSheet.DoesNotExist:
        log.debug('CharacterSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.char.MailingLists(characterID=target.owner)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    listIDs = handler.autoparse_shared_list(api_data.mailingLists,
                          MailingList,
                          ('listID',),
                          character,
                          pre_save=True)

    unsubscribed = character.mailinglist_set.exclude(listID__in=listIDs)
    for desub in unsubscribed:
        desub.owners.remove(character)

    target.updated(api_data)


@app.task(name='character.reparse_notifications')
def reparse_notifications():
    for note in Notification.objects.all():
        note.reparse()

API_MAP = {
        'ContactList': (fetch_contacts,),
        'Research': (fetch_research,),
        'MarketOrders': (fetch_marketorders,),
        'Medals': (fetch_medals,),
        'AssetList': (fetch_assetlist, fetch_blueprints),
        'WalletJournal': (fetch_walletjournal,),
        'WalletTransactions': (fetch_wallettransactions,),
        'SkillQueue': (fetch_skillqueue,),
        'SkillInTraining': (fetch_skill_in_training,),
        'Notifications': (fetch_notifications,),
        'MailMessages': (fetch_mails,),
        'MailingLists': (fetch_mailinglists,),
    }

