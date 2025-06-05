# Test Asset Library
from typing import List

from pypergraph.keyring.accounts import AssetMap, AssetLibrary
from pypergraph.keyring.models.kcs import KeyringAssetInfo

DEFAULT_FAKE: AssetMap = {
    "CUS": KeyringAssetInfo(
        id="custom_asset_id_address",
        label="Custom",
        symbol="CUS",
        network="*",
        decimals=18,
        native=True,
    )
}


class CustomAssetLibrary(AssetLibrary):
    @property
    def default_assets_map(self) -> AssetMap:
        return DEFAULT_FAKE

    @property
    def default_assets(self) -> List[str]:
        # Indicates that LTX is a default asset (perhaps a token that the app actively displays)
        return ["LTX"]


# Create an instance of the Ethereum asset library
custom_asset_library = CustomAssetLibrary()
