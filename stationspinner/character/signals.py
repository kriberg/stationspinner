from django.dispatch import Signal


character_assets_parsed = Signal(providing_args=['characterID'])
character_sheet_parsed = Signal(providing_args=['characterID'])
character_industry_jobs_updated = Signal(providing_args=['characterID'])
character_industry_jobs_history_updated = Signal(providing_args=['characterID'])