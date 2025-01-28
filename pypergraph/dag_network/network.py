from typing import Optional

from pyee.asyncio import AsyncIOEventEmitter

from pypergraph.dag_core import KeyringNetwork
from pypergraph.dag_network.api import LoadBalancerApi, BlockExplorerApi, L0Api, L1Api, ML0Api, ML1Api
from pypergraph.dag_network.models import PendingTransaction
from pypergraph.dag_wallet.models import NetworkInfo


class DagTokenNetwork(AsyncIOEventEmitter):

    def __init__(self, net_info = None):
        super().__init__()
        """Validate connected network"""
        # TODO: Do not hardcode urls
        self.connected_network = {"network": "Constellation", "network_id": "mainnet", "be_url": "https://be-mainnet.constellationnetwork.io", "l0_host": None, "cl1_host": None, "l0_lb_url": "https://l0-lb-mainnet.constellationnetwork.io", "l1_lb_url": "https://l1-lb-mainnet.constellationnetwork.io"} if not net_info else net_info
        self.network = KeyringNetwork.Constellation.value
        self.l1_lb_api = LoadBalancerApi(host=self.connected_network["l1_lb_url"])
        self.l0_lb_api = LoadBalancerApi(host=self.connected_network["l0_lb_url"])
        self.be_api = BlockExplorerApi(host=self.connected_network["be_url"])
        self.l0_api = L0Api(host=self.connected_network["l0_host"]) if self.connected_network["l0_host"] else L0Api(host=self.connected_network["l0_lb_url"])
        self.cl1_api = L1Api(host=self.connected_network["cl1_host"]) if self.connected_network["cl1_host"] else L1Api(host=self.connected_network["l1_lb_url"])
        # private networkChange$ = new Subject < NetworkInfo > ();


    def config(self, network_info: dict | None = None):
        if network_info:
            self.set_network(network_info)
        else:
            return self.get_network()

    def on_network_change(self):
        pass

    def observe_network_change(self, on_network_change):
        """Subscribe to network changes."""
        self.on('network_change', on_network_change)

    def set_network(self, network_info: dict):

        if self.connected_network != network_info:
            self.connected_network = network_info
            network_info = NetworkInfo(**network_info)
            self.be_api.config(network_info.be_url)
            self.l0_api.config(network_info.l0_host)
            self.cl1_api.config(network_info.cl1_host)

            # Emit a network change event
            self.emit('network_change', network_info.model_dump_json())

    def get_network(self):
        return self.connected_network

    async def get_address_balance(self, address: str):
        return await self.l0_api.get_address_balance(address)

    async def get_address_last_accepted_transaction_ref(self, address: str):
        return await self.cl1_api.get_last_reference(address)

    async def get_pending_transaction(self, hash: Optional[str]) -> Optional[dict]:
        pending_transaction = None
        try:
            pending_transaction = await self.cl1_api.get_pending_transaction(hash)
        except Exception as e:
            # NOOP for 404 or other exceptions
            pass
        return pending_transaction


    async def get_transactions_by_address(self, address: str, limit: Optional[int] = None,
                                          search_after: Optional[str] = None):
        response = None
        try:
            response = await self.be_api.get_transactions_by_address(address, limit, search_after)
        except Exception as e:
            # NOOP for 404 or other exceptions
            pass
        return response.get('data') if response else None


    async def get_transaction(self, hash: Optional[str]) -> Optional[dict]:
        response = None
        try:
            response = await self.be_api.get_transaction(hash)
        except Exception as e:
            # NOOP for 404 or other exceptions
            pass
        return response.get('data') if response else None


    async def post_transaction(self, tx: dict) -> str:
        response = await self.cl1_api.post_transaction(tx)
        # Support both data/meta format and object return format
        return response.get('data', {}).get('hash') or response.get('hash')


    async def get_latest_snapshot(self) -> dict:
        response = await self.be_api.get_latest_snapshot()
        return response.get('data')


class MetagraphTokenNetwork:
    def __init__(self, network_info: dict ):
        self.connected_network = {"network_id": None, "be_url": f"https://be-mainnet.constellationnetwork.io", "l0_host": None, "cl1_host": None }
        self.network_id = self.connected_network["network_id"]
        self.l0_api = ML0Api(self.connected_network["l0_url"])
        self.l1_api = ML1Api(self.connected_network["l1_url"])
        self.be_api = BlockExplorerApi(self.connected_network["be_url"])



    def get_network(self) -> dict:
        return self.connected_network

    async def get_address_balance(self, address: str) -> Optional[float]:
        return await self.l0_api.get_address_balance(address)

    async def get_address_last_accepted_transaction_ref(self, address: str) -> dict:
        return await self.l1_api.get_last_reference(address)

    async def get_pending_transaction(self, hash: Optional[str]) -> Optional[PendingTransaction]:
        pending_transaction = None
        try:
            pending_transaction = await self.l1_api.get_pending_transaction(hash)
        except Exception:
            # NOOP 404
            pass
        return pending_transaction

    async def get_transactions_by_address(
        self, address: str, limit: Optional[int] = None, search_after: Optional[str] = None
    ):
        response = None
        try:
            response = await self.be_api.get_currency_transactions_by_address(
                self.connected_network["metagraph_id"], address, limit, search_after
            )
        except Exception:
            # NOOP 404
            pass
        return response["data"] if response else None

    async def get_transaction(self, hash: Optional[str]):
        response = None
        try:
            response = await self.be_api.get_currency_transaction(self.connected_network["metagraph_id"], hash)
        except Exception:
            # NOOP 404
            pass
        return response["data"] if response else None

    async def post_transaction(self, tx) -> str:
        print("Posting transaction with the following config:", self.l1_api.__dict__)
        response = await self.l1_api.post_transaction(tx)
        # Support data/meta format and object return format
        return response["data"]["hash"] if "data" in response else response["hash"]

    async def get_latest_snapshot(self):
        response = await self.be_api.get_latest_currency_snapshot(self.connected_network["metagraph_id"])
        return response["data"]
