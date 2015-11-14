from django.dispatch import Signal


corporation_assets_parsed = Signal(providing_args=['corporationID'])
corporation_sheet_parsed = Signal(providing_args=['corporationID'])
corporation_account_balance_updated = Signal(providing_args=['corporationID'])
corporation_wallet_journal_updated = Signal(providing_args=['corporationID'])