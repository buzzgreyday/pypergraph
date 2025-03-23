from typing import Optional, Dict, List

from pypergraph.network.models.account import LastReference, Balance
from pypergraph.network.api.metagraph_layer_0_api import ML0Api
from pypergraph.network.api.metagraph_currency_layer_1_api import ML1Api
from pypergraph.network.api.metagraph_data_layer_1_api import MDL1Api
from pypergraph.network.api.block_explorer_api import BlockExplorerApi
from pypergraph.network.models.transaction import (
    PendingTransaction,
    BlockExplorerTransaction,
    SignedTransaction,
)
from pypergraph.network.models.network import NetworkInfo
import logging

# Get a logger for this specific module
logger = logging.getLogger(__name__)


class MetagraphTokenNetwork:
    """
    Network instance used to interact with Constellation Network layer 0 and
    Metagraph currency and data layers. Can be used as a separate instance or as
    'network' in MetagraphTokenClient.
    """

    def __init__(
            self,
            metagraph_id: str,
            l0_host: Optional[str] = None,
            cl1_host: Optional[str] = None,
            dl1_host: Optional[str] = None,
            network_id: Optional[str] = "mainnet",
            block_explorer: Optional[str] = None,
    ):
        # Validate connected network
        if not metagraph_id:
            raise ValueError(
                "MetagraphTokenNetwork :: Parameter 'metagraph_id' must be a valid DAG address."
            )
        self.connected_network = NetworkInfo(
            network_id=network_id,
            metagraph_id=metagraph_id,
            l0_host=l0_host,
            cl1_host=cl1_host,
            dl1_host=dl1_host,
            be_url=block_explorer,
        )
        self.be_api = (
            BlockExplorerApi(host=block_explorer)
            if block_explorer
            else BlockExplorerApi(host=self.connected_network.be_url)
        )
        # TODO: Handle optional layers
        self.l0_api = ML0Api(host=l0_host)
        self.cl1_api = ML1Api(host=cl1_host)  # Currency layer
        self.dl1_api = MDL1Api(host=dl1_host)  # Data layer

    def get_network(self) -> Dict:
        """
        Returns the MetagraphTokenNetwork NetworkInfo object as a dictionary.

        :return: Serialized NetworkInfo object.
        """
        return self.connected_network.__dict__

    async def get_address_balance(self, address: str) -> Balance:
        """
        Get the current balance of a given DAG address.

        :param address: DAG address.
        :return: Balance object.
        """
        return await self.l0_api.get_address_balance(address)

    async def get_address_last_accepted_transaction_ref(self, address: str) -> LastReference:
        """
        Get the last transaction hash and ordinal from a DAG address.

        :param address: DAG address.
        :return: Object with ordinal and hash.
        """
        return await self.cl1_api.get_last_reference(address)

    async def get_pending_transaction(self, hash: Optional[str]) -> Optional[PendingTransaction]:
        """
        Check if the given transaction is pending.

        :param hash: The transaction hash.
        :return: PendingTransaction object if found; otherwise, None.
        """
        try:
            return await self.cl1_api.get_pending_transaction(hash)
        except Exception:
            # NOOP for 404 or other exceptions
            logger.debug("No pending transaction.")
            return None

    async def get_transactions_by_address(
            self, address: str, limit: Optional[int] = None, search_after: Optional[str] = None
    ) -> Optional[List[BlockExplorerTransaction]]:
        """
        Get a paginated list of Block Explorer transaction objects.

        :param address: DAG address.
        :param limit: Limit per page.
        :param search_after: Timestamp to paginate.
        :return: List of BlockExplorerTransaction objects or None.
        """
        try:
            return await self.be_api.get_currency_transactions_by_address(
                self.connected_network.metagraph_id, address, limit, search_after
            )
        except Exception:
            # NOOP for 404 or other exceptions
            logger.debug("No transactions found.")
            return None

    async def get_transaction(self, hash: Optional[str]) -> Optional[BlockExplorerTransaction]:
        """
        Get the given transaction.

        :param hash: Transaction hash.
        :return: BlockExplorerTransaction object or None.
        """
        try:
            response = await self.be_api.get_currency_transaction(
                self.connected_network.metagraph_id, hash
            )
        except Exception:
            # NOOP for 404 or other exceptions
            logger.debug("No transaction found.")
            return None

        return response.get("data", None) if response else None

    async def get_data(self):
        """
        NOT IMPLEMENTED YET!
        Get data from Metagraph data layer 1.

        :return: Data extracted from the response or None.
        """
        try:
            response = await self.dl1_api.get_data()
        except Exception:
            # NOOP for 404 or other exceptions
            logger.debug("No data found.")
            return None

        return response.get("data", None) if response else None

    async def post_transaction(self, tx: SignedTransaction) -> str:
        """
        Post a signed transaction to Metagraph.

        :param tx: Signed transaction.
        :return: Transaction hash.
        """
        response = await self.cl1_api.post_transaction(tx)
        # Support data/meta format and object return format
        return response["data"]["hash"] if "data" in response else response["hash"]

    async def post_data(self, tx: Dict[str, Dict]) -> dict:
        """
        Post data to Metagraph. Signed transaction should be in the format:

        {
          "value": { ... },
          "proofs": [
            {
              "id": "c7f9a08bdea7ff5f51c8af16e223a1d751bac9c541125d9aef5658e9b7597aee8cba374119ebe83fb9edd8c0b4654af273f2d052e2d7dd5c6160b6d6c284a17c",
              "signature": "3045022017607e6f32295b0ba73b372e31780bd373322b6342c3d234b77bea46adc78dde022100e6ffe2bca011f4850b7c76d549f6768b88d0f4c09745c6567bbbe45983a28bf1"
            }
          ]
        }

        :param tx: Signed transaction as a dictionary.
        :return: Dictionary with response from Metagraph.
        """
        response = await self.dl1_api.post_data(tx)
        return response

    async def get_latest_snapshot(self):
        """
        Get the latest snapshot from Metagraph.

        :return: A snapshot (type currency).
        """
        response = await self.be_api.get_latest_currency_snapshot(
            self.connected_network.metagraph_id
        )
        return response
