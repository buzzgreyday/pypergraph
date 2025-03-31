from typing import List

from pypergraph.keyring.accounts.asset_library import AssetMap, AssetLibrary

# DAG (Constellation) Asset Library
# The default asset map for DAG is empty or could include a definition.
DEFAULT_DAG: AssetMap = {
    # Uncomment and adjust if a default asset is desired:
    # 'DAG': KeyringAssetInfo(
    #     id='constellation',
    #     label='Constellation',
    #     symbol='DAG',
    #     network='*',
    #     decimals=8,
    #     native=True
    # )
}

class DagAssetLibrary(AssetLibrary):
    @property
    def default_assets_map(self) -> AssetMap:
        return DEFAULT_DAG

    @property
    def default_assets(self) -> List[str]:
        return []  # No default symbols are provided in this case

# Create an instance of the DAG asset library
dag_asset_library = DagAssetLibrary()