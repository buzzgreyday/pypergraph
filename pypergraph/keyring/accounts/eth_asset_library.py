# Ethereum Asset Library
from typing import List

from pypergraph.keyring.accounts.asset_library import AssetMap, AssetLibrary
from pypergraph.keyring.models.kcs import KeyringAssetInfo

DEFAULT_ETH: AssetMap = {
    'ETH': KeyringAssetInfo(
        id='ethereum',
        label='Ethereum',
        symbol='ETH',
        network='*',
        decimals=18,
        native=True
    ),
    'LTX': KeyringAssetInfo(
        id='0xa393473d64d2F9F026B60b6Df7859A689715d092',
        address='0xa393473d64d2F9F026B60b6Df7859A689715d092',
        label='Lattice Token',
        symbol='LTX',
        network='mainnet',
        decimals=8
    )
}

class EthAssetLibrary(AssetLibrary):
    @property
    def default_assets_map(self) -> AssetMap:
        return DEFAULT_ETH

    @property
    def default_assets(self) -> List[str]:
        # Indicates that LTX is a default asset (perhaps a token that the app actively displays)
        return ['LTX']

# Create an instance of the Ethereum asset library
eth_asset_library = EthAssetLibrary()