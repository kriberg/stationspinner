from stationspinner.celery import app
from stationspinner.libs.eveapihandler import EveAPIHandler
from stationspinner.accounting.models import APIKey, APIUpdate
from stationspinner.corporation.models import CorporationSheet, AssetList, \
    MarketOrder, Medal, MemberMedal, MemberSecurity, MemberSecurityLog, \
    MemberTitle, MemberTracking, ContractItem, AccountBalance, Contact, \
    ContainerLog, Contract, ContractBid, NPCStanding, Facilities, \
    OutpostService, Shareholder, Starbase, StarbaseFuel, IndustryJob, \
    IndustryJobHistory, Outpost, WalletTransaction, WalletJournal, Asset

from celery.utils.log import get_task_logger

log = get_task_logger(__name__)


@app.task(name='corporation.fetch_corporationsheet')
def fetch_corporationsheet(apiupdate_pk):
    try:
        target = APIUpdate.objects.get(pk=apiupdate_pk)
    except APIUpdate.DoesNotExist, dne:
        log.error('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        raise dne

    apikey = target.apikey

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(apikey)
    sheet = auth.corp.CorporationSheet(characterID=apikey.characterID)

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
    return corporation.pk


@app.task(name='corporation.fetch_assetlist')
def fetch_assetlist(apiupdate_pk):
    try:
        target = APIUpdate.objects.get(pk=apiupdate_pk)
    except APIUpdate.DoesNotExist, dne:
        log.error('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        raise dne

    try:
        corporation = CorporationSheet.objects.get(pk=target.owner)
    except CorporationSheet.DoesNotExist, dne:
        log.error('Corporation {0} for APIUpdate {1} does not exist'.format(target.owner,
                                                                          target.pk))
        raise dne

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(corporation.owner_key)

    api_data = auth.corp.AssetList(characterID=corporation.owner_key.characterID)

    assetlist = AssetList(owner=corporation,
                          retrieved=api_data._meta.currentTime)

    assetlist.items = handler.asset_parser(api_data.assets,
                                           Asset,
                                           corporation)
    assetlist.save()


@app.task(name='corporation.fetch_membertracking')
def fetch_membertracking(apiupdate_pk):
    try:
        target = APIUpdate.objects.get(pk=apiupdate_pk)
    except APIUpdate.DoesNotExist, dne:
        log.error('Target APIUpdate {0} was deleted mid-flight.'.format(apiupdate_pk))
        raise dne

    try:
        corporation = CorporationSheet.objects.get(pk=target.owner)
    except CorporationSheet.DoesNotExist, dne:
        log.error('Corporation {0} for APIUpdate {1} does not exist'.format(target.owner,
                                                                          target.pk))
        raise dne

    handler = EveAPIHandler()
    auth = handler.get_authed_eveapi(corporation.owner_key)

    api_data = auth.corp.MemberTracking(characterID=corporation.owner_key.characterID,
                                        extended=1)
    handler.autoparseList(api_data.members,
                          MemberTracking,
                          unique_together=('characterID',),
                          extra_selectors={'owner': corporation},
                          owner=corporation,
                          pre_save=True)

API_MAP = [
    {
        'CorporationSheet': (fetch_corporationsheet,),
    },
    {
        'AssetList': (fetch_assetlist,),
        'MemberTrackingExtended': (fetch_membertracking,),
    }]