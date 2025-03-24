from typing import Optional, Dict, List

from rx.subject import BehaviorSubject

from pypergraph.network.models.account import Balance
from pypergraph.network.api.load_balancer_api import LoadBalancerApi
from pypergraph.network.api import Layer0Api
from pypergraph.network.api import Layer1Api
from pypergraph.network.api import BlockExplorerApi
from pypergraph.network.models.transaction import (
    PendingTransaction,
    SignedTransaction,
    TransactionReference
)
from pypergraph.network.models.block_explorer import Snapshot, Transaction
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
    ):
        # Initialize connected network info
        self.connected_network = NetworkInfo(
            network_id=network_id, l0_host=l0_host, cl1_host=cl1_host
        )
        self.l1_lb_api = LoadBalancerApi(host=self.connected_network.l1_lb_url)
        self.l0_lb_api = LoadBalancerApi(host=self.connected_network.l0_lb_url)
        self.be_api = BlockExplorerApi(host=self.connected_network.be_url)
        self.l0_api = (
            Layer0Api(host=self.connected_network.l0_host)
            if self.connected_network.l0_host
            else Layer0Api(host=self.connected_network.l0_lb_url)
        )
        self.cl1_api = (
            Layer1Api(host=self.connected_network.cl1_host)
            if self.connected_network.cl1_host
            else Layer1Api(host=self.connected_network.l1_lb_url)
        )

        self._network_change = BehaviorSubject({
            "module": "network",
            "type": "network_change",
            "event": self.get_network(),
        })

    def config(
        self,
        network_id: str = None,
        be_url: Optional[str] = None,
        l0_host: Optional[str] = None,
        cl1_host: Optional[str] = None,
        l0_lb_url: Optional[str] = None,
        l1_lb_url: Optional[str] = None,
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
            l1_lb_url=l1_lb_url,
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
            self._network_change.on_next({
                "module": "network",
                "type": "network_change",
                "event": self.get_network(),
            })

    def get_network(self) -> Dict:
        """
        Returns the DagTokenNetwork NetworkInfo object as dictionary.

        :return: Serialized NetworkInfo object.
        """
        return self.connected_network.__dict__

    async def get_address_balance(self, address: str) -> Balance:
        return await self.l0_api.get_address_balance(address)

    async def get_address_last_accepted_transaction_ref(self, address: str) -> TransactionReference:
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

    async def get_transactions_by_address(
        self,
        address: str,
        limit: Optional[int] = None,
        search_after: Optional[str] = None,
    ) -> List[Transaction]:
        """
        Get all address-specific transactions from a given timestamp.

        :param address: DAG address.
        :param limit: Limit per page.
        :param search_after: Timestamp.
        :return: List of BlockExplorerTransaction objects.
        """
        try:
            return await self.be_api.get_transactions_by_address(address, limit, search_after)
        except Exception:
            # NOOP for 404 or other exceptions
            logger.info(f"No transactions found for {address}.")

    async def get_transaction(self, hash: str) -> Transaction:
        """
        Get the given transaction from the block explorer.

        :param hash: Transaction hash.
        :return: BlockExplorerTransaction object.
        """
        try:
            return await self.be_api.get_transaction(hash)
        except Exception:
            # NOOP for 404 or other exceptions
            logger.info("DagTokenNetwork :: No transaction found.")

    async def post_transaction(self, tx: SignedTransaction) -> str:
        """
        Post a signed transaction to layer 1.

        :param tx: Signed transaction.
        :return: Transaction hash.
        """
        response = await self.cl1_api.post_transaction(tx)
        # Support both data/meta format and object return format
        return response.get("data", {}).get("hash") or response.get("hash")

    async def get_latest_snapshot(self) -> Snapshot:
        """
        Get the latest snapshot from the block explorer.

        :return: Snapshot object.
        """
        response = await self.be_api.get_latest_snapshot()
        return response
