from django.db.models.aggregates import Min
from stationspinner.celery import app
from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.accounting.models import APIUpdate
from stationspinner.universe.models import APICall
from stationspinner.corporation.models import CorporationSheet, AssetList, \
    MarketOrder, Medal, MemberMedal, MemberSecurity, MemberSecurityLog, \
    MemberTitle, MemberTracking, ContractItem, AccountBalance, Contact, \
    ContainerLog, Contract, ContractBid, NPCStanding, Facilities, \
    OutpostService, Shareholder, Starbase, StarbaseFuel, IndustryJob, \
    IndustryJobHistory, Outpost, WalletTransaction, WalletJournal, Asset, \
    Blueprint, ItemLocationName
from stationspinner.corporation.signals import \
    corporation_assets_parsed, \
    corporation_sheet_parsed, \
    corporation_account_balance_updated, \
    corporation_wallet_journal_updated
from stationspinner.libs.eveapi.eveapi import AuthenticationError
from stationspinner.libs.assethandlers import CorporationAssetHandler

from celery.utils.log import get_task_logger
from traceback import format_exc

log = get_task_logger(__name__)


def _blocker(itr, size):
    for i in xrange(0, len(itr), size):
        yield itr[i:i + size]


def _get_corporation_auth(apiupdate_pk):
    try:
        target = APIUpdate.objects.get(pk=apiupdate_pk)
    except APIUpdate.DoesNotExist, dne:
        log.error('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        raise dne

    corporation = CorporationSheet.objects.get(pk=target.owner)

    return target, corporation


@app.task(name='corporation.fetch_corporationsheet', max_retries=0)
def fetch_corporationsheet(apiupdate_pk):
    try:
        target = APIUpdate.objects.get(pk=apiupdate_pk)
    except APIUpdate.DoesNotExist, dne:
        log.error('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        raise dne

    apikey = target.apikey

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(apikey)
    try:
        sheet = auth.corp.CorporationSheet(characterID=apikey.characterID)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    try:
        corporation = CorporationSheet.objects.get(corporationID=sheet.corporationID)

        # As long as the apikey can get a valid character sheet back from the
        # eveapi, we'll allow the CS model to change owner and/or key
        if corporation.owner_key != apikey:
            log.warning('Corporation {0} "{1}" changed APIKey to keyID={2}.'.format(sheet.corporationID,
                                                                                    sheet.corporationName,
                                                                                    apikey.keyID))
        if corporation.owner != apikey.owner:
            log.warning('Corporation {0} "{1}" changed owner from "{2}" to "{3}".'.format(sheet.corporationID,
                                                                                          sheet.corporationName,
                                                                                          corporation.owner,
                                                                                          apikey.owner))
    except CorporationSheet.DoesNotExist:
        corporation = CorporationSheet(corporationID=sheet.corporationID)
    except Exception, ex:
        log.warning('Corporation {0} "{1}" could not be updated with APIKey {2}.'.format(sheet.corporationID,
                                                                                         sheet.corporationName,
                                                                                         apikey.keyID))
        raise ex

    corporation.owner_key = apikey
    corporation.owner = apikey.owner
    corporation.update_from_api(sheet, handler)

    log.info('Corporation {0} "{1}" updated.'.format(sheet.corporationID,
                                                     sheet.corporationName))
    target.updated(sheet)
    corporation_sheet_parsed.send(CorporationSheet, corporationID=corporation.pk)
    return corporation.pk


@app.task(name='corporation.fetch_assetlist', max_retries=0)
def fetch_assetlist(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(corporation.owner_key)
    try:
        api_data = auth.corp.AssetList(characterID=corporation.owner_key.characterID)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    assetlist = AssetList(owner=corporation,
                          retrieved=api_data._meta.currentTime)

    assetlist.items, itemIDs_with_names = handler.asset_parser(api_data.assets,
                                                               Asset,
                                                               corporation,
                                                               target)
    assetlist.save()

    if target.apikey.can_call(APICall.objects.get(type='Corporation',
                                                  name='Locations')):
        names_registered = 0
        log.info('Fetching the item name of {0} items for "{1}".'.format(
            len(itemIDs_with_names),
            corporation
        ))

        for block in _blocker(itemIDs_with_names, 1000):
            try:
                api_data = auth.corp.Locations(IDs=','.join(block))
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
                                         extra_selectors={'owner': corporation},
                                         owner=corporation,
                                         pre_save=True)
            names_registered += len(IDs)
        old_names = ItemLocationName.objects.filter(owner=corporation).exclude(pk__in=itemIDs_with_names)
        log.debug('Fetched {0} names and deleted {1} for "{2}"'.format(
            names_registered,
            old_names.count(),
            corporation
        ))
        old_names.delete()

    for asset in Asset.objects.filter(owner=corporation):
        asset.update_search_tokens()

    handler = CorporationAssetHandler()
    handler.invalidate_entity(corporation.pk)
    target.updated(api_data)
    corporation_assets_parsed.send(Asset, corporationID=corporation.pk)


@app.task(name='corporation.fetch_membertracking', max_retries=0)
def fetch_membertracking(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(corporation.owner_key)
    try:
        api_data = auth.corp.MemberTracking(characterID=corporation.owner_key.characterID,
                                            extended=1)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return
    memberIDs = handler.autoparse_list(api_data.members,
                                       MemberTracking,
                                       unique_together=('characterID',),
                                       extra_selectors={'owner': corporation},
                                       owner=corporation,
                                       pre_save=True)
    MemberTracking.objects.filter(owner=corporation) \
        .exclude(pk__in=memberIDs).delete()

    target.updated(api_data)


@app.task(name='corporation.fetch_starbaselist', max_retries=0)
def fetch_starbaselist(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(corporation.owner_key)
    try:
        api_data = auth.corp.StarbaseList(characterID=corporation.owner_key.characterID)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    posIDs = handler.autoparse_list(api_data.starbases,
                                    Starbase,
                                    unique_together=('itemID',),
                                    extra_selectors={'owner': corporation},
                                    owner=corporation,
                                    pre_save=True)
    Starbase.objects.filter(owner=corporation) \
        .exclude(pk__in=posIDs).delete()
    target.updated(api_data)


@app.task(name='corporation.fetch_blueprints', max_retries=0)
def fetch_blueprints(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(corporation.owner_key)

    try:
        api_data = auth.corp.Blueprints(characterID=corporation.owner_key.characterID)
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
                                           extra_selectors={'owner': corporation},
                                           owner=corporation,
                                           pre_save=True)

    Blueprint.objects.filter(owner=corporation) \
        .exclude(pk__in=blueprintsIDs).delete()
    target.updated(api_data)


@app.task(name='corporation.fetch_accountbalance', max_retries=0)
def fetch_accountbalance(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(corporation.owner_key)
    try:
        api_data = auth.corp.AccountBalance(characterID=corporation.owner_key.characterID)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return
    handler.autoparse_list(api_data.accounts,
                           AccountBalance,
                           unique_together=('accountKey',),
                           extra_selectors={'owner': corporation},
                           owner=corporation,
                           pre_save=True)
    target.updated(api_data)
    corporation_account_balance_updated.send(AccountBalance, corporationID=corporation.pk)


@app.task(name='corporation.fetch_walletjournal', max_retries=0)
def fetch_walletjournal(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    for accountKey in (1000, 1001, 1002, 1003, 1004, 1005, 1006):
        log.info('Walking accountKey {0} for corporation "{1}".'.format(accountKey, corporation))
        app.send_task('corporation.walk_walletjournal', [target.pk, None, accountKey])

    corporation_wallet_journal_updated.send(WalletJournal, corporationID=corporation.pk)

@app.task(name='corporation.walk_walletjournal', max_retries=0)
def walk_walletjournal(apiupdate_pk, fromID, accountKey):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(corporation.owner_key)
    try:
        api_data = auth.corp.WalletJournal(characterID=corporation.owner_key.characterID,
                                           accountKey=accountKey,
                                           rowCount=2560,
                                           fromID=fromID)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        return

    new_ids, overlap_ids = handler.autoparse_list(api_data.entries,
                                       WalletJournal,
                                       unique_together=['refID'],
                                       extra_selectors={'owner': corporation,
                                                        'accountKey': accountKey},
                                       owner=corporation,
                                       pre_save=True,
                                       immutable=True)
    log.info('Walked {0} wallet journal entries for corporation "{1}". {2} new entries, {3} already known'.format(
        len(new_ids)+len(overlap_ids),
        corporation,
        len(new_ids),
        len(overlap_ids)
    ))
    entry_ids = new_ids + overlap_ids
    if len(api_data.entries) >= 2560 and len(overlap_ids) < 2560:
        last_journal_entry = WalletJournal.objects.filter(owner=corporation,
                                                          accountKey=accountKey,
                                                          refID__in=entry_ids).aggregate(Min('refID'))
        app.send_task('corporation.walk_walletjournal', [target.pk,
                                                         last_journal_entry['refID__min'],
                                                         accountKey])

    target.updated(api_data)

API_MAP = {
    'AssetList': (fetch_assetlist, fetch_blueprints),
    'AccountBalance': (fetch_accountbalance,),
    'MemberTrackingExtended': (fetch_membertracking,),
    'StarbaseList': (fetch_starbaselist,),
    'WalletJournal': (fetch_walletjournal,),
}
