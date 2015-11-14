from django.dispatch import receiver
from stationspinner.celery import app
from celery.utils.log import get_task_logger
from stationspinner.character.models import CharacterSheet, Asset as ChrAsset
from stationspinner.character.signals import character_sheet_parsed, \
    character_assets_parsed
from stationspinner.corporation.models import CorporationSheet, \
    Asset as CorpAsset, AccountBalance
from stationspinner.corporation.signals import corporation_sheet_parsed, \
    corporation_assets_parsed, corporation_account_balance_updated
from stationspinner.statistics.models import WalletBalanceEntry, AssetWorthEntry

log = get_task_logger(__name__)


@app.task(name='statistics.character_asset_worth', max_retries=0)
def character_asset_worth(characterID):
    try:
        character = CharacterSheet.objects.get(pk=characterID)
    except CharacterSheet.DoesNotExist:
        log.warning('Got signal for character_assets_parsed from non-existing characterID {0}'.format(characterID))
        return

    net_worth = ChrAsset.objects.net_worth(character)

    worth = AssetWorthEntry(owner=character.pk,
                            value=net_worth)
    worth.save()


@app.task(name='statistics.character_wallet_balance', max_retries=0)
def character_wallet_balance(characterID):
    try:
        character = CharacterSheet.objects.get(pk=characterID)
    except CharacterSheet.DoesNotExist:
        log.warning('Got signal for character_sheet_parsed from non-existing characterID {0}'.format(characterID))
        return
    
    entry = WalletBalanceEntry(owner=character.pk,
                               value=character.balance)
    entry.save()


@app.task(name='statistics.corporation_asset_worth', max_retries=0)
def corporation_asset_worth(corporationID):
    try:
        corporation = CorporationSheet.objects.get(pk=corporationID)
    except CorporationSheet.DoesNotExist:
        log.warning('Got signal for corporation_assets_parsed from non-existing corporationID {0}'.format(corporationID))
        return

    net_worth = CorpAsset.objects.net_worth(corporation)

    worth = AssetWorthEntry(owner=corporation.pk,
                            value=net_worth)
    worth.save()


@app.task(name='statistics.corporation_account_balance', max_retries=0)
def corporation_account_balance(corporationID):
    try:
        corporation = CorporationSheet.objects.get(pk=corporationID)
    except CorporationSheet.DoesNotExist:
        log.warning('Got signal for corporation_account_balance_updated from non-existing corporationID {0}'.format(corporationID))
        return

    for account in AccountBalance.objects.filter(owner=corporation):
        entry = WalletBalanceEntry(owner=corporation.pk,
                                   value=account.balance,
                                   wallet_division=account.accountKey,
                                   description=account.get_division().description)
        entry.save()


@receiver(character_sheet_parsed, sender=CharacterSheet)
def trigger_character_wallet_balance(sender, characterID=None, **kwargs):
    app.send_task('statistics.character_wallet_balance', [characterID])

@receiver(character_assets_parsed, sender=ChrAsset)
def trigger_character_asset_worth(sender, characterID=None, **kwargs):
    app.send_task('statistics.character_asset_worth', [characterID])

@receiver(corporation_account_balance_updated, sender=AccountBalance)
def trigger_corporation_account_balance_updated(sender, corporationID=None, **kwargs):
    app.send_task('statistics.corporation_account_balance', [corporationID])

@receiver(corporation_assets_parsed, sender=CorpAsset)
def trigger_corporation_asset_worth(sender, corporationID=None, **kwargs):
    app.send_task('statistics.corporation_asset_worth', [corporationID])