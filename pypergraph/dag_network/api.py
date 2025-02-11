import warnings
from datetime import datetime
from typing import Optional, Any, Dict, List, Tuple

from pypergraph.dag_core.rest_api_client import RestAPIClient
from pypergraph.dag_network.models import Balance, LastReference, PendingTransaction, TotalSupply, ClusterInfo, \
    Snapshot, GlobalSnapshot


class LoadBalancerApi:
    # TODO: Data cleaning and validation for all API classes
    def __init__(self, host):
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"LoadBalancerApi :: Invalid host: {host}")
        self.service = RestAPIClient(host)

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self.service.base_url = host

    async def get_metrics(self):
        # TODO: Handle text response
        result = await self.service.get("/metrics")
        return result

    async def get_address_balance(self, address: str) -> Balance:
        result = await self.service.get(f"/dag/{address}/balance")
        result = Balance(response=result)
        return result

    async def get_last_reference(self, address) -> LastReference:
        result = await self.service.get(f"/transactions/last-reference/{address}")
        result = LastReference(response=result)
        return result

    async def get_total_supply(self) -> TotalSupply:
        result = await self.service.get('/total-supply')
        result = TotalSupply(response=result)
        return result

    async def post_transaction(self, tx: Dict[str, Any]):
        result = await self.service.post("/transactions", payload=tx)
        return result

    async def get_pending_transaction(self, tx_hash: str):
        result = await self.service.get(f"/transactions/{tx_hash}")
        result = PendingTransaction(response=result)
        return result

    async def get_cluster_info(self) -> [ClusterInfo, ...]:
        result = await self.service.get("/cluster/info")
        result = ClusterInfo.process_cluster_info(response=result)
        return result


class BlockExplorerApi:

    def __init__(self, host):
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"BlockExplorerApi :: Invalid host: {host}")
        self.service = RestAPIClient(host)

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL dynamically."""
        self.service.base_url = host

    async def get_snapshot(self, id: str | int) -> Snapshot:
        result = await self.service.get(f"/global-snapshots/{id}")
        result = Snapshot(response=result)
        return result

    async def get_transactions_by_snapshot(self, id: str | int):
        result = await self.service.get(f"/global-snapshots/{id}/transactions")
        return result

    async def get_rewards_by_snapshot(self, id: str | int):
        result = await self.service.get(f"/global-snapshots/{id}/rewards")
        return result

    async def get_latest_snapshot(self) -> Snapshot:
        result = await self.service.get("/global-snapshots/latest")

        result = Snapshot(response=result["data"])
        return result

    async def get_latest_snapshot_transaction(self):
        result = await self.service.get("/global-snapshots/latest/transactions")
        return result

    async def get_latest_snapshot_rewards(self):
        result = await self.service.get("/global-snapshots/latest/rewards")
        return result

    def _format_date(self, date: datetime, param_name: str) -> str:
        try:
            return date.isoformat()
        except Exception:
            raise ValueError(f'ParamError: "{param_name}" is not valid ISO 8601')

    def _get_transaction_search_path_and_params(
            self, base_path: str, limit: Optional[int], search_after: Optional[str],
            sent_only: bool, received_only: bool, search_before: Optional[str]
    ) -> Dict:
        params = {}
        path = base_path

        if limit or search_after or search_before:
            if limit and limit > 0:
                params["limit"] = limit
            if search_after:
                params["search_after"] = search_after
            elif search_before:
                params["search_before"] = search_before

        if sent_only:
            path += '/sent'
        elif received_only:
            path += '/received'

        return {"path": path, "params": params}

    async def get_transactions(
            self, limit: Optional[int], search_after: Optional[str],
            search_before: Optional[str]
    ) -> List[Dict]:
        base_path = "/transactions"
        result = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        return await self.service.get(result["path"], result["params"])

    async def get_transactions_by_address(
            self, address: str, limit: int = 0, search_after: str = '',
            sent_only: bool = False, received_only: bool = False, search_before: str = ''
    ) -> List[Dict]:
        base_path = f"/addresses/{address}/transactions"
        result = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, sent_only, received_only, search_before
        )
        return await self.service.get(result["path"], result["params"])

    async def get_transaction(self, hash: str) -> Dict:
        return await self.service.get(f"/transactions/{hash}")

    async def get_address_balance(self, hash: str) -> Balance:
        result = await self.service.get(f"/addresses/{hash}/balance")
        result = Balance(response=result)
        return result

    async def get_checkpoint_block(self, hash: str) -> Dict:
        return await self.service.get(f"/blocks/{hash}")

    async def get_latest_currency_snapshot(self, metagraph_id: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/snapshots/latest")

    async def get_currency_snapshot(self, metagraph_id: str, hash_or_ordinal: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}")

    async def get_latest_currency_snapshot_rewards(self, metagraph_id: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/snapshots/latest/rewards")

    async def get_currency_snapshot_rewards(
            self, metagraph_id: str, hash_or_ordinal: str
    ) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}/rewards")

    async def get_currency_block(self, metagraph_id: str, hash: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/blocks/{hash}")

    async def get_currency_address_balance(self, metagraph_id: str, hash: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/addresses/{hash}/balance")

    async def get_currency_transaction(self, metagraph_id: str, hash: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/transactions/{hash}")

    async def get_currency_transactions(
            self, metagraph_id: str, limit: Optional[int], search_after: Optional[str],
            search_before: Optional[str]
    ) -> List[Dict]:
        base_path = f"/currency/{metagraph_id}/transactions"
        result = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        return await self.service.get(result["path"], result["params"])

    async def get_currency_transactions_by_address(
            self, metagraph_id: str, address: str, limit: int = 0, search_after: str = '',
            sent_only: bool = False, received_only: bool = False, search_before: str = ''
    ) -> List[Dict]:
        base_path = f"/currency/{metagraph_id}/addresses/{address}/transactions"
        result = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, sent_only, received_only, search_before
        )
        return await self.service.get(result["path"], result["params"])

    async def get_currency_transactions_by_snapshot(
            self, metagraph_id: str, hash_or_ordinal: str, limit: int = 0,
            search_after: str = '', search_before: str = ''
    ) -> List[Dict]:
        base_path = f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}/transactions"
        result = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        return await self.service.get(result["path"], result["params"])


class L0Api:

    def __init__(self, host):
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"L0Api :: Invalid host: {host}")
        self.service = RestAPIClient(host)

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL dynamically."""
        self.service.base_url = host

    async def get_cluster_info(self):
        result = await self.service.get("/cluster/info")
        result = ClusterInfo.process_cluster_info(response=result)
        return result

    # Metrics
    async def get_metrics(self):
        # TODO: Data clean up - parsing
        return await self.service.get("/metrics")

    # DAG
    async def get_total_supply(self):
        result = await self.service.get("/dag/total-supply")
        result = TotalSupply(response=result)
        return result

    async def get_total_supply_at_ordinal(self, ordinal: int):
        result = await self.service.get(f"/dag/{ordinal}/total-supply")
        result = TotalSupply(response=result)
        return result

    async def get_address_balance(self, address: str):
        result = await self.service.get(f"/dag/{address}/balance")
        result = Balance(response=result)
        return result

    async def get_address_balance_at_ordinal(self, ordinal: int, address: str):
        return await self.service.get(f"/dag/{ordinal}/{address}/balance")

    # Global Snapshot
    async def get_latest_snapshot(self) -> GlobalSnapshot:
        result = await self.service.get(
            "/global-snapshots/latest"
        )
        result = GlobalSnapshot(response=result)
        return result

    async def get_latest_snapshot_ordinal(self):
        return await self.service.get("/global-snapshots/latest/ordinal")

    async def get_snapshot(self, id: str | int) -> Snapshot:
        result = await self.service.get(
                     f"/global-snapshots/{id}"
                 )
        result = Snapshot(result)
        return result

    # State Channels
    async def post_state_channel_snapshot(self, address: str, snapshot: dict):
        return await self.service.post(
            f"/state-channel/{address}/snapshot",
            payload=snapshot
        )

class L1Api:

    def __init__(self, host):
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"L0Api :: Invalid host: {host}")
        self.service = RestAPIClient(host)

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL dynamically."""
        self.service.base_url = host

    async def get_cluster_info(self) -> [ClusterInfo, ...]:
        result = await self.service.get("/cluster/info")
        result = ClusterInfo.process_cluster_info(response=result)
        return result

    # Metrics
    async def get_metrics(self):
        # TODO: add parsing for v2 response... returns 404
        return await self.service.get("/metrics")

    # Transactions
    async def get_last_reference(self, address: str) -> LastReference:
        result = await self.service.get(f"/transactions/last-reference/{address}")
        result = LastReference(response=result)
        return result

    async def get_pending_transaction(self, hash: str) -> PendingTransaction:
        result = await self.service.get(f"/transactions/{hash}")
        result = PendingTransaction(response=result)
        return result

    async def post_transaction(self, tx):
        return await self.service.post("/transactions", payload=tx)

class ML0Api(L0Api):
    def __init__(self, host):
        super().__init__(host)

    def config(self, net_info: dict):
        """Reconfigure the RestAPIClient's base URL dynamically."""
        self.service.base_url = net_info

    # State Channel Token
    async def get_total_supply(self) -> TotalSupply:
        result = await self.service.get("/currency/total-supply")
        result = TotalSupply(response=result)
        return result

    async def get_total_supply_at_ordinal(self, ordinal: int) -> TotalSupply:
        result = await self.service.get(f"/currency/{ordinal}/total-supply")
        result = TotalSupply(response=result)
        return result

    async def get_address_balance(self, address: str):
        return await self.service.get(f"/currency/{address}/balance")

    async def get_address_balance_at_ordinal(self, ordinal: int, address: str):
        return await self.service.get(f"/currency/{ordinal}/{address}/balance")


class ML1Api(L1Api):
    def __init__(self, host):
        super().__init__(host)

