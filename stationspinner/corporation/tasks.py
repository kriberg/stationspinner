from django.db.models.aggregates import Min
from stationspinner.celery import app
from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.accounting.models import APIUpdate
from stationspinner.universe.models import APICall
from stationspinner.corporation.models import CorporationSheet, AssetList, \
    MarketOrder, Medal, MemberMedal, MemberSecurity, MemberSecurityLog, \
    MemberTitle, MemberTracking, ContractItem, AccountBalance, Contact, \
    ContainerLog, Contract, ContractBid, NPCStanding, Facility, \
    OutpostService, Shareholder, Starbase, StarbaseFuel, IndustryJob, \
    IndustryJobHistory, Outpost, WalletTransaction, WalletJournal, Asset, \
    Blueprint, ItemLocationName, CustomsOffice
from stationspinner.corporation.signals import \
    corporation_corporation_sheet_added, \
    corporation_assets_parsed, \
    corporation_sheet_parsed, \
    corporation_account_balance_updated, \
    corporation_wallet_journal_updated, \
    corporation_container_log_updated, \
    corporation_customs_offices_updated, \
    corporation_industry_jobs_updated, \
    corporation_industry_jobs_history_updated, \
    corporation_contact_list_updated, \
    corporation_member_security_log_updated, \
    corporation_shareholders_updated, \
    corporation_market_orders_updated, \
    corporation_member_security_updated, \
    corporation_member_security_new_role, \
    corporation_member_security_new_title, \
    corporation_medals_updated, \
    corporation_member_medals_updated, \
    corporation_member_tracking_updated, \
    corporation_starbases_updated, \
    corporation_starbase_details_updated, \
    corporation_facilities_updated, \
    corporation_contracts_updated, \
    corporation_contract_bids_new_bid, \
    corporation_contract_bids_updated, \
    corporation_contract_items_updated
from stationspinner.libs.eveapi.eveapi import AuthenticationError, ServerError
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
        created = False
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
        created = True
    except Exception, ex:
        log.warning('Corporation {0} "{1}" could not be updated with APIKey {2}.'.format(sheet.corporationID,
                                                                                         sheet.corporationName,
                                                                                         apikey.keyID))
        raise ex

    corporation.owner_key = apikey
    corporation.owner = apikey.owner
    corporation.update_from_api(sheet, handler)
    if created:
        corporation_corporation_sheet_added.send(CorporationSheet,
                                                 corporationID=corporation.corporationID)

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
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.AssetList(characterID=target.apikey.characterID)
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
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.MemberTracking(characterID=target.apikey.characterID,
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
    corporation_member_tracking_updated.send(Starbase, corporationID=corporation.pk)


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
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.StarbaseList()
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
                                    owner=corporation)
    Starbase.objects.filter(owner=corporation).exclude(pk__in=posIDs).delete()

    target.updated(api_data)
    corporation_starbases_updated.send(Starbase, corporationID=corporation.pk)

    try:
        details_call = APICall.objects.get(type='Corporation',
                                           name='StarbaseDetail')
        details_target = APIUpdate.objects.get(apicall=details_call,
                                               apikey=target.apikey,
                                               owner=target.owner)
        for starbase_pk in posIDs:
            app.send_task('corporation.fetch_starbasedetails', (details_target.pk, starbase_pk))
    except APICall.DoesNotExist:
        log.error('Could not find APICall for StarbaseDetails.')
    except APIUpdate.DoesNotExist:
        log.debug('Key {0} cant call starbase details, so its starbases remain undetailed.'.format(
            target.apikey.keyID
        ))


@app.task(name='corporation.fetch_starbasedetails', max_retries=0)
def fetch_starbasedetails(apiupdate_pk, starbase_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    try:
        starbase = Starbase.objects.get(owner=corporation, pk=starbase_pk)
    except Starbase.DoesNotExist:
        log.warning('Received request for starbase details on non-existant starbase {0} owned by {1}.'.format(
            starbase_pk,
            corporation,
        ))
        return

    # Unanchored starbases dont have details, just wait for somebody to anchor it first.
    if starbase.state == 0:
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)

    try:
        api_data = auth.corp.StarbaseDetail(itemID=starbase.itemID)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return
    except ServerError:
        log.error('ServerError while getting starbase details for {0} with apikey {1}.'.format(
            starbase.itemID,
            target.apikey.keyID
        ))
        return

    fuel_ids = handler.autoparse_list(api_data.fuel,
                                      StarbaseFuel,
                                      unique_together=('starbase', 'typeID'),
                                      extra_selectors={'owner': corporation},
                                      owner=corporation,
                                      static_defaults={
                                          'starbase': starbase
                                      })
    StarbaseFuel.objects.filter(owner=corporation,
                                starbase=starbase).exclude(pk__in=fuel_ids).delete()

    target.updated(api_data)
    corporation_starbase_details_updated.send(Starbase, corporationID=corporation.pk, starbase_pk=starbase.pk)


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
    auth = handler.get_authed_eveapi(target.apikey)

    try:
        api_data = auth.corp.Blueprints()
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
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.AccountBalance()
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
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.WalletJournal(characterID=target.apikey.characterID,
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


@app.task(name='corporation.fetch_containerlog', max_retries=0)
def fetch_containerlog(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.ContainerLog()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    handler.autoparse_list(api_data.containerLog,
                           ContainerLog,
                           unique_together=('logTime', 'itemID'),
                           extra_selectors={'owner': corporation},
                           owner=corporation,
                           immutable=True)
    target.updated(api_data)
    corporation_container_log_updated.send(ContainerLog, corporationID=corporation.pk)


@app.task(name='corporation.fetch_customsoffices', max_retries=0)
def fetch_customsoffices(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.CustomsOffices()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    handler.autoparse_list(api_data.pocos,
                           CustomsOffice,
                           unique_together=('solarSystemID', 'itemID'),
                           extra_selectors={'owner': corporation},
                           owner=corporation)
    target.updated(api_data)
    corporation_customs_offices_updated.send(CustomsOffice, corporationID=corporation.pk)


@app.task(name='corporation.fetch_industryjobs', max_retries=0)
def fetch_industryjobs(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.IndustryJobs()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    handler.autoparse_list(api_data.jobs,
                           IndustryJob,
                           unique_together=('jobID', ),
                           extra_selectors={'owner': corporation},
                           owner=corporation)
    target.updated(api_data)
    corporation_industry_jobs_updated.send(IndustryJob, corporationID=corporation.pk)


@app.task(name='corporation.fetch_industryjobshistory', max_retries=0)
def fetch_industryjobshistory(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.IndustryJobsHistory()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    handler.autoparse_list(api_data.jobs,
                           IndustryJobHistory,
                           unique_together=('jobID', ),
                           extra_selectors={'owner': corporation},
                           owner=corporation)
    target.updated(api_data)
    corporation_industry_jobs_history_updated.send(IndustryJobHistory, corporationID=corporation.pk)


@app.task(name='corporation.fetch_contactlist', max_retries=0)
def fetch_contactlist(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.ContactList()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    corp_ids = handler.autoparse_list(api_data.corporateContactList,
                                      Contact,
                                      unique_together=('contactID',),
                                      extra_selectors={'owner': corporation},
                                      owner=corporation,
                                      static_defaults={'listType': 'Corporate'})

    ally_ids = handler.autoparse_list(api_data.allianceContactList,
                                      Contact,
                                      unique_together=('contactID',),
                                      extra_selectors={'owner': corporation},
                                      owner=corporation,
                                      static_defaults={'listType': 'Alliance'})
    old_entries = Contact.objects.filter(owner=corporation).exclude(pk__in=corp_ids+ally_ids)
    deleted = old_entries.count()
    old_entries.delete()
    log.info('Updated standings for corporation "{0}". {1} entries, {2} old entries removed.'.format(
        corporation,
        len(corp_ids) + len(ally_ids),
        deleted
    ))

    target.updated(api_data)
    corporation_contact_list_updated.send(Contact, corporationID=corporation.pk)


@app.task(name='corporation.fetch_membersecuritylog', max_retries=0)
def fetch_membersecuritylog(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.MemberSecurityLog()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    handler.autoparse_list(api_data.roleHistory,
                           MemberSecurityLog,
                           unique_together=('changeTime', 'characterID', 'roleLocationType'),
                           extra_selectors={'owner': corporation},
                           owner=corporation,
                           immutable=True)

    target.updated(api_data)
    corporation_member_security_log_updated.send(MemberSecurityLog, corporationID=corporation.pk)


@app.task(name='corporation.fetch_shareholders', max_retries=0)
def fetch_shareholders(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.ShareHolders()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    char_ids = handler.autoparse_list(api_data.characters,
                                      Shareholder,
                                      unique_together=('shareholderID', 'holder_type'),
                                      extra_selectors={'owner': corporation},
                                      owner=corporation,
                                      static_defaults={'holder_type': 'Character'})

    corp_ids = handler.autoparse_list(api_data.corporations,
                                      Shareholder,
                                      unique_together=('shareholderID', 'holder_type'),
                                      extra_selectors={'owner': corporation},
                                      owner=corporation,
                                      static_defaults={'holder_type': 'Corporation'})

    old_entries = Shareholder.objects.filter(owner=corporation).exclude(pk__in=char_ids+corp_ids)
    deleted = old_entries.count()
    old_entries.delete()
    log.info('Updated shareholders for corporation "{0}". {1} entries, {2} old entries removed.'.format(
        corporation,
        len(corp_ids) + len(char_ids),
        deleted
    ))

    target.updated(api_data)
    corporation_shareholders_updated.send(Shareholder, corporationID=corporation.pk)


@app.task(name='corporation.fetch_marketorders', max_retries=0)
def fetch_marketorders(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.MarketOrders()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    handler.autoparse_list(api_data.orders,
                           MarketOrder,
                           unique_together=('orderID', ),
                           extra_selectors={'owner': corporation},
                           owner=corporation)

    target.updated(api_data)
    corporation_market_orders_updated.send(MarketOrder, corporationID=corporation.pk)


@app.task(name='corporation.fetch_membersecurity', max_retries=0)
def fetch_membersecurity(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.MemberSecurity()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return
    role_ids = []
    title_ids = []
    for member in api_data.members:
        for role_type  in MemberSecurity.ROLE_LOCATION:
            role_type = role_type[0]
            if role_type == 'Global':
                name_key = 'roles'
                grant_key = 'grantableRoles'
            else:
                name_key = 'rolesAt{0}'.format(role_type)
                grant_key = 'grantableRolesAt{0}'.format(role_type)
            for role in getattr(member, name_key):
                obj, created = MemberSecurity.objects.update_or_create(characterID=member.characterID,
                                                                       owner=corporation,
                                                                       roleID=role.roleID,
                                                                       location=role_type,
                                                                       defaults={
                                                                           'roleID': role.roleID,
                                                                           'roleName': role.roleName,
                                                                           'characterID': member.characterID,
                                                                           'characterName': member.name,
                                                                           'location': role_type,
                                                                           'owner': corporation
                                                                       })
                role_ids.append(obj.pk)
                if created:
                    corporation_member_security_new_role.send(MemberSecurity,
                                                              corporationID=corporation.pk,
                                                              member_security_pk=obj.pk)
            for grantable in getattr(member, grant_key):
                obj, created = MemberSecurity.objects.update_or_create(characterID=member.characterID,
                                                                       owner=corporation,
                                                                       roleID=grantable.roleID,
                                                                       location=role_type,
                                                                       defaults={
                                                                           'roleID': grantable.roleID,
                                                                           'roleName': grantable.roleName,
                                                                           'characterID': member.characterID,
                                                                           'characterName': member.name,
                                                                           'location': role_type,
                                                                           'grantable': True,
                                                                           'owner': corporation
                                                                       })
                role_ids.append(obj.pk)
                if created:
                    corporation_member_security_new_role.send(MemberSecurity,
                                                              corporationID=corporation.pk,
                                                              member_security_pk=obj.pk)
        for title in member.titles:
            obj, created = MemberTitle.objects.update_or_create(owner=corporation,
                                                                characterID=member.characterID,
                                                                titleID=title.titleID,
                                                                defaults={
                                                                    'titleID': title.titleID,
                                                                    'titleName': title.titleName,
                                                                    'characterID': member.characterID,
                                                                    'characterName': member.name,
                                                                    'owner': corporation
                                                                })
            title_ids.append(obj.pk)
            if created:
                corporation_member_security_new_title.send(MemberTitle,
                                                           corporationID=corporation.pk,
                                                           member_title_pk=obj.pk)



    old_roles = MemberSecurity.objects.filter(owner=corporation).exclude(pk__in=role_ids)
    roles_deleted = old_roles.count()
    old_roles.delete()
    old_titles = MemberTitle.objects.filter(owner=corporation).exclude(pk__in=title_ids)
    titles_deleted = old_titles.count()
    old_titles.delete()
    log.info('Updated roles and titles for "{0}": {1} roles granted, {2} removed. {3} titles set, {4} removed.'.format(
        corporation,
        len(role_ids),
        roles_deleted,
        len(title_ids),
        titles_deleted
    ))

    target.updated(api_data)
    corporation_member_security_updated.send(MemberSecurity, corporationID=corporation.pk)


@app.task(name='corporation.fetch_medals', max_retries=0)
def fetch_medals(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.Medals()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    medal_ids = handler.autoparse_list(api_data.medals,
                                       Medal,
                                       unique_together=('medalID',),
                                       extra_selectors={'owner': corporation},
                                       owner=corporation)

    Medal.objects.filter(owner=corporation).exclude(pk__in=medal_ids).delete()
    target.updated(api_data)
    corporation_medals_updated.send(Medal, corporationID=corporation.pk)


@app.task(name='corporation.fetch_membermedals', max_retries=0)
def fetch_membermedals(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.MemberMedals()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    medal_ids = handler.autoparse_list(api_data.issuedMedals,
                                       MemberMedal,
                                       unique_together=('medalID', 'characterID'),
                                       extra_selectors={'owner': corporation},
                                       owner=corporation)

    MemberMedal.objects.filter(owner=corporation).exclude(pk__in=medal_ids).delete()
    target.updated(api_data)
    corporation_member_medals_updated.send(MemberMedal, corporationID=corporation.pk)


@app.task(name='corporation.fetch_wallettransactions', max_retries=0)
def fetch_wallettransactions(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    log.info('Walking transactions for corporation "{0}".'.format(corporation))
    app.send_task('corporation.walk_wallettransactions', [target.pk, None])
    corporation_wallet_journal_updated.send(WalletTransaction, corporationID=corporation.pk)


@app.task(name='corporation.walk_wallettransactions', max_retries=0)
def walk_wallettransactions(apiupdate_pk, fromID):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.WalletTransactions(characterID=target.apikey.characterID,
                                                rowCount=2560,
                                                fromID=fromID)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
                target.apikey.keyID,
                target.apikey.owner
        ))
        return

    new_ids, overlap_ids = handler.autoparse_list(api_data.transactions,
                                                  WalletTransaction,
                                                  unique_together=['transactionID'],
                                                  extra_selectors={'owner': corporation},
                                                  owner=corporation,
                                                  immutable=True)
    log.info('Walked {0} wallet transaction entries for corporation "{1}". {2} new entries, {3} already known'.format(
            len(new_ids) + len(overlap_ids),
            corporation,
            len(new_ids),
            len(overlap_ids)
    ))
    entry_ids = new_ids + overlap_ids
    if len(api_data.transactions) >= 2560 and len(overlap_ids) < 2560:
        last_transaction_entry = WalletTransaction.objects.filter(owner=corporation,
                                                              transactionID__in=entry_ids).aggregate(
                Min('transactionID'))
        app.send_task('corporation.walk_wallettransactions', [target.pk,
                                                              last_transaction_entry['transactionID__min']])

    target.updated(api_data)


@app.task(name='corporation.fetch_facilities', max_retries=0)
def fetch_facilities(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.Facilities()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    facility_ids = handler.autoparse_list(api_data.facilities,
                                          Facility,
                                          unique_together=('facilityID', ),
                                          extra_selectors={'owner': corporation},
                                          owner=corporation)

    Facility.objects.filter(owner=corporation).exclude(pk__in=facility_ids).delete()
    target.updated(api_data)
    corporation_facilities_updated.send(Facility, corporationID=corporation.pk)


@app.task(name='corporation.fetch_contracts', max_retries=0)
def fetch_contracts(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.Contracts()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    contract_ids = handler.autoparse_list(api_data.contractList,
                                          Contract,
                                          unique_together=('contractID',),
                                          extra_selectors={'owner': corporation},
                                          owner=corporation)

    target.updated(api_data)
    corporation_contracts_updated.send(Contract, corporationID=corporation.pk)

    for id in contract_ids:
        contract = Contract.objects.get(pk=id)
        if contract.get_items().count() == 0:
            app.send_task('corporation.fetch_contractitems', [target.pk, contract.pk])


@app.task(name='corporation.fetch_contractitems', max_retries=0)
def fetch_contractitems(apiupdate_pk, contract_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    try:
        contract = Contract.objects.get(pk=contract_pk,
                                        owner=corporation)
    except Contract.DoesNotExist:
        log.warning('ContractItems requested for non-existing contractID {0} with APIUpdate {1}.'.format(
            contract_pk,
            apiupdate_pk
        ))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.ContractItems(contractID=contract.contractID)
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    handler.autoparse_list(api_data.itemList,
                           ContractItem,
                           unique_together=('contract', 'recordID'),
                           extra_selectors={'owner': corporation},
                           owner=corporation,
                           immutable=True,
                           static_defaults={
                               'contract': contract
                           })

    target.updated(api_data)
    corporation_contract_items_updated.send(ContractItem, corporationID=corporation.pk, contract_pk=contract.pk)


@app.task(name='corporation.fetch_contractbids', max_retries=0)
def fetch_contractbids(apiupdate_pk):
    try:
        target, corporation = _get_corporation_auth(apiupdate_pk)
    except CorporationSheet.DoesNotExist:
        log.debug('CorporationSheet for APIUpdate {0} not indexed yet.'.format(apiupdate_pk))
        return
    except APIUpdate.DoesNotExist:
        log.warning('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        return

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(target.apikey)
    try:
        api_data = auth.corp.ContractBids()
    except AuthenticationError:
        log.error('AuthenticationError for key "{0}" owned by "{1}"'.format(
            target.apikey.keyID,
            target.apikey.owner
        ))
        target.delete()
        return

    bid_ids, overlap = handler.autoparse_list(api_data.bidList,
                                              ContractBid,
                                              unique_together=('contractID', 'bidID'),
                                              extra_selectors={'owner': corporation},
                                              owner=corporation,
                                              immutable=True)

    target.updated(api_data)
    # Only trigger if there are new bids
    for bid in ContractBid.objects.filter(pk__in=bid_ids):
        corporation_contract_bids_new_bid.send(ContractBid,
                                               corporationID=corporation.pk,
                                               contractID=bid.contractID,
                                               bid_pk = bid.pk)
    corporation_contract_bids_updated.send(ContractBid, corporationID=corporation.pk)



API_MAP = {
    'AssetList': (fetch_assetlist, fetch_blueprints, fetch_customsoffices, fetch_facilities),
    'AccountBalance': (fetch_accountbalance,),
    'MemberTrackingExtended': (fetch_membertracking,),
    'StarbaseList': (fetch_starbaselist,),
    'StarbaseDetail': tuple(),
    'WalletJournal': (fetch_walletjournal,),
    'ContainerLog': (fetch_containerlog, ),
    'IndustryJobs': (fetch_industryjobs, fetch_industryjobshistory),
    'ContactList': (fetch_contactlist, ),
    'MemberSecurityLog': (fetch_membersecuritylog, ),
    'Shareholders': (fetch_shareholders, ),
    'MarketOrders': (fetch_marketorders, ),
    'MemberSecurity': (fetch_membersecurity, ),
    'Medals': (fetch_medals, ),
    'MemberMedals': (fetch_membermedals, ),
    'WalletTransactions': (fetch_wallettransactions, ),
    'Contracts': (fetch_contracts, fetch_contractbids)
}
