from typing import Optional, Dict, List

from rx.subject import BehaviorSubject

from pypergraph.network.models.account import LastReference, Balance
from pypergraph.network.load_balancer_api import LoadBalancerApi
from pypergraph.network.layer_0_api import L0Api
from pypergraph.network.metagraph_layer_0_api import ML0Api
from pypergraph.network.metagraph_currency_layer_1_api import ML1Api
from pypergraph.network.layer_1_api import L1Api
from pypergraph.network.block_explorer_api import BlockExplorerApi
from pypergraph.network.models.transaction import PendingTransaction, BlockExplorerTransaction, \
    SignedTransaction
from pypergraph.network.models.snapshot import Snapshot
from pypergraph.network.models.network import NetworkInfo
from pypergraph.core.exceptions import NetworkError
import logging

# Get a logger for this specific module
logger = logging.getLogger(__name__)

class DagTokenNetwork:
    def __init__(
        self,
        network_id: str = "mainnet",
        l0_host: Optional[str] = None,
        cl1_host: Optional[str] = None,
        scheduler: Optional = None  # Injected scheduler for testing or production
    ):
        # Initialize connected network info
        self.connected_network = NetworkInfo(network_id=network_id, l0_host=l0_host, cl1_host=cl1_host)
        self.l1_lb_api = LoadBalancerApi(host=self.connected_network.l1_lb_url)
        self.l0_lb_api = LoadBalancerApi(host=self.connected_network.l0_lb_url)
        self.be_api = BlockExplorerApi(host=self.connected_network.be_url)
        self.l0_api = (
            L0Api(host=self.connected_network.l0_host)
            if self.connected_network.l0_host
            else L0Api(host=self.connected_network.l0_lb_url)
        )
        self.cl1_api = (
            L1Api(host=self.connected_network.cl1_host)
            if self.connected_network.cl1_host
            else L1Api(host=self.connected_network.l1_lb_url)
        )

        self._network_change = BehaviorSubject({"module": "network", "type": "network_change", "event": self.get_network()})

    def config(
        self,
        network_id: str = None,
        be_url: Optional[str] = None,
        l0_host: Optional[str] = None,
        cl1_host: Optional[str] = None,
        l0_lb_url: Optional[str] = None,
        l1_lb_url: Optional[str] = None
    ):
        """
        Reconfigure the network; new configuration is applied only if different from the current one.
        """
        new_info = NetworkInfo(
            network_id=network_id,
            be_url=be_url,
            l0_host=l0_host,
            cl1_host=cl1_host,
            l0_lb_url=l0_lb_url,
            l1_lb_url=l1_lb_url
        )
        self.set_network(new_info)

    def set_network(self, network_info: NetworkInfo):
        if network_info.network_id not in ("mainnet", "integrationnet", "testnet", None):
            raise ValueError("DagTokenNetwork :: Invalid network id.")
        if self.connected_network.__dict__ != network_info.__dict__:
            self.connected_network = network_info
            self.be_api.config(network_info.be_url)  # Block Explorer
            self.l0_api.config(network_info.l0_host)
            self.l0_lb_api.config(network_info.l0_lb_url)
            self.l1_lb_api.config(network_info.l1_lb_url)
            self.cl1_api.config(network_info.cl1_host)  # Currency layer

            # Emit a network change event
            self._network_change.on_next({"module": "network", "type": "network_change", "event": self.get_network()})


    def get_network(self) -> Dict:
        """
        Returns the DagTokenNetwork NetworkInfo object as dictionary.

        :return: Serialized NetworkInfo object.
        """
        return self.connected_network.__dict__

    async def get_address_balance(self, address: str) -> Balance:
        return await self.l0_api.get_address_balance(address)

    async def get_address_last_accepted_transaction_ref(self, address: str) -> LastReference:
        """
        Get the last transaction hash and ordinal from DAG address.

        :param address:
        :return: Object with ordinal and transaction hash.
        """
        return await self.cl1_api.get_last_reference(address)

    async def get_pending_transaction(self, hash: str) -> PendingTransaction:
        """
        Check if the given transaction is pending.

        :param hash:
        :return: Object if transaction is pending, else log error.
        """
        try:
            return await self.cl1_api.get_pending_transaction(hash)
        except NetworkError as e:
            # NOOP for 404 or other exceptions
            if e.status == 404:
                logger.debug("No transaction pending.")
            else:
                logger.error(f"{e}")
                raise e


    async def get_transactions_by_address(self, address: str, limit: Optional[int] = None,
                                          search_after: Optional[str] = None) -> List[BlockExplorerTransaction]:
        """
        Get all address specific transaction from timestamp.

        :param address: DAG address.
        :param limit: Limit per page.
        :param search_after: Timestamp.
        :return: List of block explorer transaction objects.
        """
        try:
            return await self.be_api.get_transactions_by_address(address, limit, search_after)
        except Exception:
            # NOOP for 404 or other exceptions
            logger.info(f"No transactions found for {address}.")



    async def get_transaction(self, hash: str) -> BlockExplorerTransaction:
        """
        Get the given transaction from block explorer.

        :param hash: Transaction hash.
        :return: Block explorer transaction object.
        """
        try:
            return await self.be_api.get_transaction(hash)
        except Exception:
            # NOOP for 404 or other exceptions
            logger.info("No transaction found.")


    async def post_transaction(self, tx: SignedTransaction) -> str:
        """
        Post a signed transaction to layer 1.

        :param tx: Signed transaction.
        :return: Transaction hash.
        """
        response = await self.cl1_api.post_transaction(tx)
        # Support both data/meta format and object return format
        return response.get('data', {}).get('hash') or response.get('hash')


    async def get_latest_snapshot(self) -> Snapshot:
        """
        Get the latest snapshot from block explorer.

        :return: Snapshot object.
        """
        response = await self.be_api.get_latest_snapshot()
        return response


class MetagraphTokenNetwork:
    """
    Network instance used to interact with Constellation Network layer 0 and Metagraph currency and data layer. Can be used as a separate instance or as 'network' in MetagraphTokenClient..

    """
    def __init__(
            self, metagraph_id: str, l0_host: Optional[str] = None, cl1_host: Optional[str] = None,
            dl1_host: Optional[str] = None, network_id: Optional[str] = "mainnet", block_explorer: Optional[str] = None
    ):
        super().__init__()
        """Validate connected network"""
        if not metagraph_id:
            raise ValueError("MetagraphTokenNetwork :: Parameter 'metagraph_id' must be a valid DAG address.")
        self.connected_network = NetworkInfo(network_id=network_id, metagraph_id=metagraph_id, l0_host=l0_host, cl1_host=cl1_host, dl1_host=dl1_host, be_url=block_explorer)
        self.be_api = BlockExplorerApi(host=block_explorer) if block_explorer else BlockExplorerApi(host=self.connected_network.be_url)
        self.l0_api = ML0Api(host=l0_host)
        self.cl1_api = ML1Api(host=cl1_host) # Currency layer
        self.dl1_api = MDL1Api(host=dl1_host) # Data layer


    def get_network(self) -> Dict:
        """
        Returns the DagTokenNetwork NetworkInfo object as dictionary.

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
        Get the last transaction hash and ordinal from DAG address.

        :param address: DAG address.
        :return: Object with ordinal and hash.
        """
        return await self.cl1_api.get_last_reference(address)

    async def get_pending_transaction(self, hash: Optional[str]) -> Optional[PendingTransaction]:
        """
        Check if the given transaction is pending.

        :param hash: The transaction hash.
        :return: Object if transaction is pending, else log error.
        """
        pending_transaction = None
        try:
            pending_transaction = await self.cl1_api.get_pending_transaction(hash)
        except Exception:
            # NOOP 404
            logger.debug("No pending transaction.")
        return pending_transaction

    async def get_transactions_by_address(
        self, address: str, limit: Optional[int] = None, search_after: Optional[str] = None
    ) -> Optional[List[BlockExplorerTransaction]]:
        """
        Get paginated list of Block Explorer transaction objects.

        :param address: DAG address.
        :param limit: Limit per page.
        :param search_after: Timestamp.
        :return:
        """
        try:
            return await self.be_api.get_currency_transactions_by_address(
                self.connected_network.metagraph_id, address, limit, search_after
            )
        except Exception:
            # NOOP 404
            logger.debug(f"No transactions found.")

    async def get_transaction(self, hash: Optional[str]) -> Optional[BlockExplorerTransaction]:
        """
        Get the given transaction.

        :param hash: Transaction hash.
        :return: Block explorer transaction object or None.
        """
        response = None
        try:
            response = await self.be_api.get_currency_transaction(self.connected_network.metagraph_id, hash)
        except Exception:
            # NOOP 404
            logger.debug("No transaction found.")
        return response.get("data", None)

    async def get_data(self):
        """
        NOT IMPLEMENTED YET!
        Get data from Metagraph data layer 1.

        :return:
        """
        response = None
        try:
            response = await self.dl1_api.get_data()
        except Exception:
            # NOOP 404
            logger.debug("No transaction found.")
        return response.get("data", None)

    async def post_transaction(self, tx: SignedTransaction) -> str:
        """
        Post signed transaction to Metagraph.

        :param tx: Signed transaction.
        :return:  Transaction hash.
        """
        response = await self.cl1_api.post_transaction(tx)
        # Support data/meta format and object return format
        return response["data"]["hash"] if "data" in response else response["hash"]

    async def post_data(self, tx: Dict[str, Dict]) -> dict:
        """
        Post data to Metagraph. Signed transaction:
        {
          "value": { ... },
          "proofs": [
            {
              "id": "c7f9a08bdea7ff5f51c8af16e223a1d751bac9c541125d9aef5658e9b7597aee8cba374119ebe83fb9edd8c0b4654af273f2d052e2d7dd5c6160b6d6c284a17c",
              "signature": "3045022017607e6f32295b0ba73b372e31780bd373322b6342c3d234b77bea46adc78dde022100e6ffe2bca011f4850b7c76d549f6768b88d0f4c09745c6567bbbe45983a28bf1"
            }
          ]
        }

        :param tx: Signed transaction as dictionary.
        :return: Dictionary with response from Metagraph.
        """
        response = await self.dl1_api.post_data(tx)
        # Support data/meta format and object return format
        return response

    async def get_latest_snapshot(self):
        """
        Get the latest snapshot from Metagraph.

        :return: A snapshot (type currency).
        """
        response = await self.be_api.get_latest_currency_snapshot(self.connected_network.metagraph_id)
        return response
