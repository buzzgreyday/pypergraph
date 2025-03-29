from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pypergraph.keyring.models.kcs import KeyringAssetInfo

# AssetMap is a dictionary mapping a token symbol to its KeyringAssetInfo.
AssetMap = Dict[str, KeyringAssetInfo]

class AssetLibrary(ABC):
    def __init__(self):
        # This holds tokens that are imported at runtime.
        self.imported_assets: AssetMap = {}

    @property
    @abstractmethod
    def default_assets_map(self) -> AssetMap:
        """Returns the default asset map (i.e., a dict mapping symbols to asset info)."""
        pass

    @property
    @abstractmethod
    def default_assets(self) -> List[str]:
        """Returns a list of default asset symbols."""
        pass

    def serialize(self) -> AssetMap:
        """Serializes (or exports) the imported assets for saving state."""
        return self.imported_assets

    def deserialize(self, assets: AssetMap) -> None:
        """Loads a previously saved asset map."""
        self.imported_assets = assets

    def get_default_assets(self) -> List[str]:
        """Returns a copy of the default asset symbols."""
        return self.default_assets[:]

    def get_asset_by_symbol(self, symbol: str) -> Optional[KeyringAssetInfo]:
        """
        Looks up an asset by symbol.
        First checks the default assets, then any imported tokens.
        """
        return self.default_assets_map.get(symbol) or self.imported_assets.get(symbol)

    def import_token(self, token: KeyringAssetInfo) -> bool:
        """
        Imports a new token.
        Returns True if the token was added (i.e. did not exist before),
        otherwise returns False.
        """
        if token.symbol not in self.imported_assets:
            self.imported_assets[token.symbol] = token
            return True
        return False