from django.dispatch import Signal


accounting_new_character = Signal(providing_args=['apikey_pk', 'characterID'])
accounting_new_corporation = Signal(providing_args=['apikey_pk', 'corporationID'])