from django.dispatch import Signal


corporation_assets_parsed = Signal(providing_args=['corporationID'])
corporation_sheet_parsed = Signal(providing_args=['corporationID'])
corporation_account_balance_updated = Signal(providing_args=['corporationID'])
corporation_wallet_journal_updated = Signal(providing_args=['corporationID'])
corporation_container_log_updated = Signal(providing_args=['corporationID'])
corporation_customs_offices_updated = Signal(providing_args=['corporationID'])
corporation_industry_jobs_updated = Signal(providing_args=['corporationID'])
corporation_industry_jobs_history_updated = Signal(providing_args=['corporationID'])
corporation_contact_list_updated = Signal(providing_args=['corporationID'])
corporation_member_security_log_updated = Signal(providing_args=['corporationID'])
corporation_shareholders_updated = Signal(providing_args=['corporationID'])
corporation_market_orders_updated = Signal(providing_args=['corporationID'])
corporation_member_security_updated = Signal(providing_args=['corporationID'])
corporation_member_security_new_role = Signal(providing_args=['corporationID', 'member_security_pk'])
corporation_member_security_new_title = Signal(providing_args=['corporationID', 'member_title_pk'])