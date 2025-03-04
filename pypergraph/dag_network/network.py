from typing import Optional, Dict, List

from pyee.asyncio import AsyncIOEventEmitter

from pypergraph.dag_network.models.account import LastReference, Balance
from pypergraph.dag_network.api import LoadBalancerApi, BlockExplorerApi, L0Api, L1Api, ML0Api, ML1Api, MDL1Api
from pypergraph.dag_network.models.transaction import PendingTransaction, BlockExplorerTransaction, \
    SignedTransaction
from pypergraph.dag_network.models.snapshot import Snapshot
from pypergraph.dag_network.models.network import NetworkInfo
from pypergraph.dag_core.exceptions import NetworkError
import logging

# Get a logger for this specific module
logger = logging.getLogger(__name__)

class DagTokenNetwork(AsyncIOEventEmitter):

    def __init__(self, network_id: str = "mainnet", l0_host: Optional[str] = None, cl1_host: Optional[str] = None):
        super().__init__()
        """Validate connected network"""
        # TODO: Do not hardcode urls
        self.connected_network = NetworkInfo(network_id=network_id, l0_host=l0_host, cl1_host=cl1_host)
        self.l1_lb_api = LoadBalancerApi(host=self.connected_network.l1_lb_url)
        self.l0_lb_api = LoadBalancerApi(host=self.connected_network.l0_lb_url)
        self.be_api = BlockExplorerApi(host=self.connected_network.be_url)
        self.l0_api = L0Api(host=self.connected_network.l0_host) if self.connected_network.l0_host else L0Api(host=self.connected_network.l0_lb_url)
        self.cl1_api = L1Api(host=self.connected_network.cl1_host) if self.connected_network.cl1_host else L1Api(host=self.connected_network.l1_lb_url)
        # private networkChange$ = new Subject < NetworkInfo > ();


    def config(self, network_id: str = None, be_url: Optional[str] = None, l0_host: Optional[str] = None, cl1_host: Optional[str] = None, l0_lb_url: Optional[str] = None, l1_lb_url: Optional[str] = None):
        """
        Configure a new NetworkInfo object to setup network_id, l0, l1, be, etc. (default: "mainnet" configuration)

        :param network_id:
        :param be_url:
        :param l0_host:
        :param cl1_host:
        :param l0_lb_url:
        :param l1_lb_url:
        :return:
        """
        self.set_network(NetworkInfo(network_id=network_id, be_url=be_url, l0_host=l0_host, cl1_host=cl1_host, l0_lb_url=l0_lb_url, l1_lb_url=l1_lb_url))


    def on_network_change(self):
        pass

    def observe_network_change(self, on_network_change):
        """Subscribe to network changes."""
        self.on('network_change', on_network_change)

    def set_network(self, network_info: NetworkInfo):

        if self.connected_network.__dict__ != network_info.__dict__:
            self.connected_network = network_info
            self.be_api.config(network_info.be_url)
            self.l0_api.config(network_info.l0_host)
            self.l0_lb_api.config(network_info.l0_lb_url)
            self.l1_lb_api.config(network_info.l1_lb_url)
            self.cl1_api.config(network_info.cl1_host)

            # Emit a network change event
            self.emit('network_change', network_info.__dict__)

    def get_network(self) -> Dict:
        """
        Returns the DagTokenNetwork NetworkInfo object as dictionary.

        :return: Serialized NetworkInfo object.
        """
        return self.connected_network.__dict__

    async def get_address_balance(self, address: str) -> Balance:
        return await self.l0_api.get_address_balance(address)

    async def get_address_last_accepted_transaction_ref(self, address: str) -> LastReference:
        return await self.cl1_api.get_last_reference(address)

    async def get_pending_transaction(self, hash: str) -> PendingTransaction:
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
        try:
            return await self.be_api.get_transactions_by_address(address, limit, search_after)
        except Exception:
            # NOOP for 404 or other exceptions
            logger.warning("No transaction found.")



    async def get_transaction(self, hash: str) -> BlockExplorerTransaction:
        try:
            return await self.be_api.get_transaction(hash)
        except Exception:
            # NOOP for 404 or other exceptions
            logger.warning("No transaction found.")


    async def post_transaction(self, tx: SignedTransaction) -> str:
        response = await self.cl1_api.post_transaction(tx)
        # Support both data/meta format and object return format
        return response.get('data', {}).get('hash') or response.get('hash')


    async def get_latest_snapshot(self) -> Snapshot:
        response = await self.be_api.get_latest_snapshot()
        return response


class MetagraphTokenNetwork(AsyncIOEventEmitter):

    def __init__(self, metagraph_id: str, l0_host: str, cl1_host: str, dl1_host: str, network_id: str = "mainnet", block_explorer: Optional[str] = None):
        super().__init__()
        """Validate connected network"""
        # TODO: Do not hardcode urls
        if not metagraph_id:
            raise ValueError("MetagraphTokenNetwork :: Parameters.")
        self.connected_network = NetworkInfo(network_id=network_id, metagraph_id=metagraph_id, l0_host=l0_host, cl1_host=cl1_host, dl1_host=dl1_host, be_url=block_explorer)
        self.be_api = BlockExplorerApi(host=block_explorer) if block_explorer else BlockExplorerApi(host=self.connected_network.be_url)
        self.l0_api = ML0Api(host=l0_host)
        self.cl1_api = ML1Api(host=cl1_host)
        self.dl1_api = MDL1Api(host=dl1_host)


    def get_network(self) -> Dict:
        """
        Returns the DagTokenNetwork NetworkInfo object as dictionary.

        :return: Serialized NetworkInfo object.
        """
        return self.connected_network.__dict__


    async def get_address_balance(self, address: str) -> Balance:
        return await self.l0_api.get_address_balance(address)

    async def get_address_last_accepted_transaction_ref(self, address: str) -> LastReference:
        return await self.cl1_api.get_last_reference(address)

    async def get_pending_transaction(self, hash: Optional[str]) -> Optional[PendingTransaction]:
        pending_transaction = None
        try:
            pending_transaction = await self.cl1_api.get_pending_transaction(hash)
        except Exception:
            # NOOP 404
            logger.debug("No pending transaction.")
        return pending_transaction

    async def get_transactions_by_address(
        self, address: str, limit: Optional[int] = None, search_after: Optional[str] = None
    ) -> List[BlockExplorerTransaction]:
        try:
            return await self.be_api.get_currency_transactions_by_address(
                self.connected_network.metagraph_id, address, limit, search_after
            )
        except Exception:
            # NOOP 404
            logger.debug("No transaction found.")

    async def get_transaction(self, hash: Optional[str]):
        response = None
        try:
            response = await self.be_api.get_currency_transaction(self.connected_network.metagraph_id, hash)
        except Exception:
            # NOOP 404
            logger.debug("No transaction found.")
        return response.get("data", None)

    async def get_data(self):
        response = None
        try:
            response = await self.dl1_api.get_data()
        except Exception:
            # NOOP 404
            logger.debug("No transaction found.")
        return response.get("data", None)

    async def post_transaction(self, tx: SignedTransaction) -> str:
        response = await self.cl1_api.post_transaction(tx)
        # Support data/meta format and object return format
        return response["data"]["hash"] if "data" in response else response["hash"]

    async def post_data(self, tx: Dict) -> dict:
        response = await self.dl1_api.post_data(tx)
        # Support data/meta format and object return format
        return response

    async def get_latest_snapshot(self):
        response = await self.be_api.get_latest_currency_snapshot(self.connected_network.metagraph_id)
        return response
