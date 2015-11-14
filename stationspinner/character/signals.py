from django.dispatch import Signal


character_assets_parsed = Signal(providing_args=['characterID'])
character_sheet_parsed = Signal(providing_args=['characterID'])