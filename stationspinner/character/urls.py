from django.conf.urls import url, include
from rest_framework import routers
from stationspinner.character.views import CharacterSheetViewset, \
    NotificationViewset, MailMessageViewset, DistinctAllianceViewset, \
    DistinctCorporationViewset, WalletTransactionsViewset, \
    AssetLocationsView, AssetsView, AssetSearchView

router = routers.DefaultRouter()
router.register(r'CharacterSheet', CharacterSheetViewset, 'CharacterSheet')
router.register(r'Notifications', NotificationViewset, 'Notifications')
router.register(r'MailMessage', MailMessageViewset, 'MailMessage')
router.register(r'DistinctCorporations', DistinctCorporationViewset, 'DistinctCorporations')
router.register(r'DistinctAlliances', DistinctAllianceViewset, 'DistinctAlliances')
router.register(r'WalletTransactions', WalletTransactionsViewset, 'WalletTransactions')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^Assets', AssetsView.as_view(), name='character_assets'),
    url(r'^AssetLocations', AssetLocationsView.as_view(), name='character_asset_locations'),
    url(r'^AssetSearch', AssetSearchView.as_view(), name='character_asset_search'),
]
