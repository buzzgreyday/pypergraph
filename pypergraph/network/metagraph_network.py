from typing import Optional, Dict, List

from pypergraph.core.cross_platform.di.rest_client import RESTClient
from pypergraph.network.models.account import Balance
from pypergraph.network.models.transaction import TransactionReference
from pypergraph.network.api import MetagraphLayer0Api
from pypergraph.network.api import MetagraphCurrencyLayerApi
from pypergraph.network.api import MetagraphDataLayerApi
from pypergraph.network.api.block_explorer_api import BlockExplorerApi
from pypergraph.network.models.transaction import (
    PendingTransaction,
    SignedTransaction,
)
from pypergraph.network.models.network import NetworkInfo
from pypergraph.network.models.block_explorer import Transaction
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
            currency_l1_host: Optional[str] = None,
            data_l1_host: Optional[str] = None,
            network_id: Optional[str] = "mainnet",
            block_explorer: Optional[str] = None,
            client: Optional[RESTClient] = None
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
            currency_l1_host=currency_l1_host,
            data_l1_host=data_l1_host,
            block_explorer_url=block_explorer
        )
        self.be_api = (
            BlockExplorerApi(host=block_explorer, client=client)
            if block_explorer
            else BlockExplorerApi(host=self.connected_network.block_explorer_url, client=client)
        )
        self.l0_api = MetagraphLayer0Api(host=l0_host, client=client) if l0_host else None
        self.cl1_api = MetagraphCurrencyLayerApi(host=currency_l1_host, client=client)  if currency_l1_host else None # Currency layer
        self.dl1_api = MetagraphDataLayerApi(host=data_l1_host, client=client) if data_l1_host else None # Data layer

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
        try:
            return await self.l0_api.get_address_balance(address)
        except AttributeError:
            logging.warning("MetagraphTokenNetwork :: Layer 0 API object not set.")

    async def get_address_last_accepted_transaction_ref(self, address: str) -> TransactionReference:
        """
        Get the last transaction hash and ordinal from a DAG address.

        :param address: DAG address.
        :return: Object with ordinal and hash.
        """
        try:
            return await self.cl1_api.get_last_reference(address)
        except AttributeError:
            logging.warning("MetagraphTokenNetwork :: Currency layer 1 API object not set.")

    async def get_pending_transaction(self, hash: Optional[str]) -> Optional[PendingTransaction]:
        """
        Check if the given transaction is pending.

        :param hash: The transaction hash.
        :return: PendingTransaction object if found; otherwise, None.
        """
        try:
            return await self.cl1_api.get_pending_transaction(hash)
        except AttributeError:
            logging.warning("MetagraphTokenNetwork :: Currency layer 1 API object not set.")
        except Exception:
            # NOOP for 404 or other exceptions
            logger.debug("No pending transaction.")
            return None

    async def get_transactions_by_address(
            self, address: str, limit: Optional[int] = None, search_after: Optional[str] = None
    ) -> Optional[List[Transaction]]:
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
            logger.debug("MetagraphTokenNetwork :: No transactions found.")
            return None

    async def get_transaction(self, hash: Optional[str]) -> Optional[Transaction]:
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
        # TODO: is it return in "data" key?
        try:
            response = await self.dl1_api.get_data()
        except AttributeError:
            logging.warning("MetagraphTokenNetwork :: Data layer 1 API object not set.")
        except Exception:
            # NOOP for 404 or other exceptions
            logger.debug("No data found.")
            return None
        else:
            return response.get("data", None) if response else None

    async def post_transaction(self, tx: SignedTransaction) -> str:
        """
        Post a signed transaction to Metagraph.

        :param tx: Signed transaction.
        :return: Transaction hash.
        """
        try:
            response = await self.cl1_api.post_transaction(tx)
            # Support data/meta format and object return format
            return response["data"]["hash"] if "data" in response else response["hash"]
        except AttributeError:
            logging.warning("MetagraphTokenNetwork :: Currency layer 1 API object not set.")

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
        try:
            response = await self.dl1_api.post_data(tx)
            return response
        except AttributeError:
            logging.warning("MetagraphTokenNetwork :: Data layer 1 API object not set.")

    async def get_latest_snapshot(self):
        """
        Get the latest snapshot from Metagraph.

        :return: A snapshot (type currency).
        """
        response = await self.be_api.get_latest_currency_snapshot(
            self.connected_network.metagraph_id
        )
        return response
