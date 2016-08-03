from django.conf.urls import url#, include
#from rest_framework import routers
from stationspinner.statistics.views import CharacterAssetSummaryView, \
    CorporationAssetSummaryView, \
    CharacterWalletBalanceView, \
    CorporationWalletBalanceView, \
    CharacterAssetWorthView

#router = routers.DefaultRouter()
#router.register(r'CharacterAssetWorth', CharacterAssetWorthViewset, 'CharacterAssetWorth')

urlpatterns = [
    #url(r'^', include(router.urls)),
    url(r'^CharacterAssetSummary', CharacterAssetSummaryView.as_view(), name='statistics_character_asset_summary'),
    url(r'^CorporationAssetSummary', CorporationAssetSummaryView.as_view(), name='statistics_corporation_asset_summary'),
    url(r'^CharacterWalletBalance', CharacterWalletBalanceView.as_view(), name='statistics_character_wallet_balance'),
    url(r'^CorporationWalletBalance', CorporationWalletBalanceView.as_view(), name='statistics_corporation_wallet_balance'),
    url(r'^CharacterAssetWorth', CharacterAssetWorthView.as_view(), name='statistics_character_asset_worth'),
]
