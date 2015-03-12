from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.character.views import CharacterSheetViewset, \
    NotificationViewset, MailMessageViewset, DistinctAllianceViewset, \
    DistinctCorporationViewset, WalletTransactionsViewset

router = routers.DefaultRouter()
router.register(r'CharacterSheet', CharacterSheetViewset, 'CharacterSheet')
router.register(r'Notifications', NotificationViewset, 'Notifications')
router.register(r'MailMessage', MailMessageViewset, 'MailMessage')
router.register(r'DistinctCorporations', DistinctCorporationViewset, 'DistinctCorporations')
router.register(r'DistinctAlliances', DistinctAllianceViewset, 'DistinctAlliances')
router.register(r'WalletTransactions', WalletTransactionsViewset, 'WalletTransactions')

urlpatterns = [
    url(r'^', include(router.urls)),
]