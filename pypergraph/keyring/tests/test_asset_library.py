# Test Asset Library
from typing import List

from pypergraph.keyring.accounts import AssetMap, AssetLibrary
from pypergraph.keyring.models.kcs import KeyringAssetInfo

DEFAULT_FAKE: AssetMap = {
    'FAKE1': KeyringAssetInfo(
        id='fakereum1',
        label='Fakereum1',
        symbol='FAKE1',
        network='*',
        decimals=18,
        native=True
    )
}

class FakeAssetLibrary(AssetLibrary):
    @property
    def default_assets_map(self) -> AssetMap:
        return DEFAULT_FAKE

    @property
    def default_assets(self) -> List[str]:
        # Indicates that LTX is a default asset (perhaps a token that the app actively displays)
        return ['LTX']

# Create an instance of the Ethereum asset library
fake_asset_library = FakeAssetLibrary()