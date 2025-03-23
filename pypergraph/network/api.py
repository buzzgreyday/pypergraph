from typing import Optional, Any, Dict, List, Union
from prometheus_client.parser import text_string_to_metric_families

from pypergraph.network.models.reward import Reward
from pypergraph.core.rest_api_client import RestAPIClient
from pypergraph.network.models.account import Balance, LastReference
from pypergraph.network.models.transaction import (
    PendingTransaction,
    BlockExplorerTransaction,
    SignedTransaction,
)
from pypergraph.network.models.network import TotalSupply, PeerInfo
from pypergraph.network.models.snapshot import Snapshot, GlobalSnapshot, CurrencySnapshot, Ordinal


def _handle_metrics(response: str) -> List[Dict[str, Any]]:
    """
    Parse Prometheus metrics output from a text response.

    :param response: Prometheus text output.
    :return: List of dictionaries with metric details.
    """
    metrics = []
    for family in text_string_to_metric_families(response):
        for sample in family.samples:
            metrics.append({
                "name": sample[0],
                "labels": sample[1],
                "value": sample[2],
                "type": family.type,
            })
    return metrics


class LoadBalancerApi:
    def __init__(self, host: str):
        self._service = RestAPIClient(host) if host else None

    @property
    def service(self) -> RestAPIClient:
        if not self._service:
            raise ValueError("LoadBalancerApi :: Load balancer host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)

    async def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics of a random node (served by the LB).

        :return: Prometheus output as a list of dictionaries.
        """
        response = await self.service.get("/metrics")
        return _handle_metrics(response)

    async def get_address_balance(self, address: str) -> Balance:
        result = await self.service.get(f"/dag/{address}/balance")
        return Balance(**result, meta=result.get("meta"))

    async def get_last_reference(self, address: str) -> LastReference:
        result = await self.service.get(f"/transactions/last-reference/{address}")
        return LastReference(**result)

    async def get_total_supply(self) -> TotalSupply:
        result = await self.service.get("/total-supply")
        return TotalSupply(**result)

    async def post_transaction(self, tx: Dict[str, Any]):
        result = await self.service.post("/transactions", payload=tx)
        return result

    async def get_pending_transaction(self, tx_hash: str) -> PendingTransaction:
        result = await self.service.get(f"/transactions/{tx_hash}")
        return PendingTransaction(**result)

    async def get_cluster_info(self) -> List[PeerInfo]:
        result = await self.service.get("/cluster/info")
        return PeerInfo.process_cluster_peers(data=result)


class BlockExplorerApi:
    def __init__(self, host: str):
        self._service = RestAPIClient(host) if host else None

    @property
    def service(self) -> RestAPIClient:
        if not self._service:
            raise ValueError("BlockExplorerApi :: Block explorer host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL dynamically."""
        self._service = RestAPIClient(host)

    async def get_snapshot(self, id: Union[str, int]) -> Snapshot:
        """
        Retrieve a snapshot by its hash or ordinal.

        :param id: Hash or ordinal identifier.
        :return: Snapshot object.
        """
        result = await self.service.get(f"/global-snapshots/{id}")
        return Snapshot(**result["data"])

    async def get_transactions_by_snapshot(self, id: Union[str, int]) -> List[BlockExplorerTransaction]:
        """
        Retrieve transactions for a given snapshot.

        :param id: Hash or ordinal identifier.
        :return: List of BlockExplorerTransaction objects.
        """
        results = await self.service.get(f"/global-snapshots/{id}/transactions")
        return BlockExplorerTransaction.process_transactions(
            data=results["data"],
            meta=results.get("meta"),
        )

    async def get_rewards_by_snapshot(self, id: Union[str, int]) -> List[Reward]:
        """
        Retrieve reward objects for a given snapshot.

        :param id: Hash or ordinal.
        :return: List of Reward objects.
        """
        results = await self.service.get(f"/global-snapshots/{id}/rewards")
        return Reward.process_snapshot_rewards(results["data"])

    async def get_latest_snapshot(self) -> Snapshot:
        """
        Get the latest snapshot from the block explorer.

        :return: Snapshot object.
        """
        result = await self.service.get("/global-snapshots/latest")
        return Snapshot(**result["data"])

    async def get_latest_snapshot_transactions(self) -> List[BlockExplorerTransaction]:
        """
        Retrieve transactions for the latest snapshot.

        :return: List of BlockExplorerTransaction objects.
        """
        results = await self.service.get("/global-snapshots/latest/transactions")
        return BlockExplorerTransaction.process_transactions(
            data=results.get("data"),
            meta=results.get("meta"),
        )

    async def get_latest_snapshot_rewards(self) -> List[Reward]:
        results = await self.service.get("/global-snapshots/latest/rewards")
        return Reward.process_snapshot_rewards(results["data"])

    @staticmethod
    def _get_transaction_search_path_and_params(
        base_path: str,
        limit: Optional[int],
        search_after: Optional[str],
        sent_only: bool,
        received_only: bool,
        search_before: Optional[str],
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
            path += "/sent"
        elif received_only:
            path += "/received"

        return {"path": path, "params": params}

    async def get_transactions(
        self,
        limit: Optional[int],
        search_after: Optional[str] = None,
        search_before: Optional[str] = None,
    ) -> List[BlockExplorerTransaction]:
        """
        Get transactions from the block explorer. Supports pagination.

        :param limit: Maximum number of transactions.
        :param search_after: Pagination parameter.
        :param search_before: Pagination parameter.
        :return: List of BlockExplorerTransaction objects.
        """
        base_path = "/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        results = await self.service.get(endpoint=request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(
            data=results.get("data"),
            meta=results.get("meta"),
        )

    async def get_transactions_by_address(
        self,
        address: str,
        limit: int = 0,
        search_after: str = "",
        sent_only: bool = False,
        received_only: bool = False,
        search_before: str = "",
    ) -> List[BlockExplorerTransaction]:
        """
        Retrieve transactions for a specific DAG address. Supports pagination.

        :param address: DAG address.
        :param limit: Maximum number of transactions.
        :param search_after: Pagination parameter.
        :param sent_only: Filter for sent transactions.
        :param received_only: Filter for received transactions.
        :param search_before: Pagination parameter.
        :return: List of BlockExplorerTransaction objects.
        """
        base_path = f"/addresses/{address}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, sent_only, received_only, search_before
        )
        results = await self.service.get(endpoint=request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(
            data=results.get("data"),
            meta=results.get("meta"),
        )

    async def get_transaction(self, hash: str) -> BlockExplorerTransaction:
        """
        Retrieve a transaction by its hash.

        :param hash: Transaction hash.
        :return: BlockExplorerTransaction object.
        """
        result = await self.service.get(f"/transactions/{hash}")
        return BlockExplorerTransaction(**result["data"], meta=result.get("meta"))

    async def get_address_balance(self, hash: str) -> Balance:
        """
        Retrieve the balance for a given address from the block explorer.

        :param hash: Address hash.
        :return: Balance object.
        """
        result = await self.service.get(f"/addresses/{hash}/balance")
        return Balance(**result["data"], meta=result.get("meta"))

    async def get_latest_currency_snapshot(self, metagraph_id: str) -> CurrencySnapshot:
        result = await self.service.get(f"/currency/{metagraph_id}/snapshots/latest")
        return CurrencySnapshot(**result["data"], meta=result.get("meta"))

    async def get_currency_snapshot(self, metagraph_id: str, hash_or_ordinal: str) -> CurrencySnapshot:
        result = await self.service.get(f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}")
        return CurrencySnapshot(**result["data"], meta=result.get("meta"))

    async def get_latest_currency_snapshot_rewards(self, metagraph_id: str) -> List[Reward]:
        result = await self.service.get(f"/currency/{metagraph_id}/snapshots/latest/rewards")
        return Reward.process_snapshot_rewards(data=result["data"])

    async def get_currency_snapshot_rewards(self, metagraph_id: str, hash_or_ordinal: str) -> List[Reward]:
        results = await self.service.get(f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}/rewards")
        return Reward.process_snapshot_rewards(data=results["data"])

    async def get_currency_address_balance(self, metagraph_id: str, hash: str) -> Balance:
        result = await self.service.get(f"/currency/{metagraph_id}/addresses/{hash}/balance")
        return Balance(**result["data"], meta=result.get("meta"))

    async def get_currency_transaction(self, metagraph_id: str, hash: str) -> BlockExplorerTransaction:
        result = await self.service.get(f"/currency/{metagraph_id}/transactions/{hash}")
        return BlockExplorerTransaction(**result["data"], meta=result.get("meta"))

    async def get_currency_transactions(
        self,
        metagraph_id: str,
        limit: Optional[int],
        search_after: Optional[str] = None,
        search_before: Optional[str] = None,
    ) -> List[BlockExplorerTransaction]:
        base_path = f"/currency/{metagraph_id}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        results = await self.service.get(endpoint=request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results["data"])

    async def get_currency_transactions_by_address(
        self,
        metagraph_id: str,
        address: str,
        limit: int = 0,
        search_after: str = "",
        sent_only: bool = False,
        received_only: bool = False,
        search_before: str = "",
    ) -> List[BlockExplorerTransaction]:
        base_path = f"/currency/{metagraph_id}/addresses/{address}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, sent_only, received_only, search_before
        )
        results = await self.service.get(endpoint=request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results["data"])

    async def get_currency_transactions_by_snapshot(
        self,
        metagraph_id: str,
        hash_or_ordinal: str,
        limit: int = 0,
        search_after: str = "",
        search_before: str = "",
    ) -> List[BlockExplorerTransaction]:
        base_path = f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        results = await self.service.get(endpoint=request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results["data"])


class L0Api:
    def __init__(self, host: str):
        self._service = RestAPIClient(host) if host else None

    @property
    def service(self) -> RestAPIClient:
        if not self._service:
            raise ValueError("L0Api :: Layer 0 host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)

    async def get_cluster_info(self) -> List[PeerInfo]:
        result = await self.service.get("/cluster/info")
        return PeerInfo.process_cluster_peers(data=result)

    async def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics from the L0 endpoint.

        :return: Prometheus output as a list of dictionaries.
        """
        response = await self.service.get("/metrics")
        return _handle_metrics(response)

    async def get_total_supply(self) -> TotalSupply:
        result = await self.service.get("/dag/total-supply")
        return TotalSupply(**result)

    async def get_address_balance(self, address: str) -> Balance:
        result = await self.service.get(f"/dag/{address}/balance")
        return Balance(**result, meta=result.get("meta"))

    async def get_latest_snapshot(self) -> GlobalSnapshot:
        result = await self.service.get("/global-snapshots/latest")
        return GlobalSnapshot(**result)

    async def get_latest_snapshot_ordinal(self) -> Ordinal:
        result = await self.service.get("/global-snapshots/latest/ordinal")
        return Ordinal(**result)

    async def post_state_channel_snapshot(self, address: str, snapshot: dict):
        # TODO: Add validation
        return await self.service.post(f"/state-channel/{address}/snapshot", payload=snapshot)


class L1Api:
    def __init__(self, host: str):
        self._service = RestAPIClient(host) if host else None

    @property
    def service(self) -> RestAPIClient:
        if not self._service:
            raise ValueError("L1Api :: Currency layer 1 host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)

    async def get_cluster_info(self) -> List[PeerInfo]:
        result = await self.service.get("/cluster/info")
        return PeerInfo.process_cluster_peers(data=result)

    async def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics from the L1 endpoint.

        :return: Prometheus output as a list of dictionaries.
        """
        response = await self.service.get("/metrics")
        return _handle_metrics(response)

    async def get_last_reference(self, address: str) -> LastReference:
        result = await self.service.get(f"/transactions/last-reference/{address}")
        return LastReference(**result)

    async def get_pending_transaction(self, hash: str) -> PendingTransaction:
        result = await self.service.get(f"/transactions/{hash}")
        return PendingTransaction(**result)

    async def post_transaction(self, tx: SignedTransaction):
        return await self.service.post("/transactions", payload=tx.model_dump())


class ML0Api(L0Api):
    def __init__(self, host: str):
        super().__init__(host)

    @property
    def service(self) -> RestAPIClient:
        if not self._service:
            raise ValueError("ML0Api :: Metagraph layer 0 host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)

    async def get_total_supply(self) -> TotalSupply:
        result = await self.service.get("/currency/total-supply")
        return TotalSupply(**result)

    async def get_total_supply_at_ordinal(self, ordinal: int) -> TotalSupply:
        result = await self.service.get(f"/currency/{ordinal}/total-supply")
        return TotalSupply(**result)

    async def get_address_balance(self, address: str) -> Balance:
        result = await self.service.get(f"/currency/{address}/balance")
        return Balance(**result, meta=result.get("meta"))

    async def get_address_balance_at_ordinal(self, ordinal: int, address: str) -> Balance:
        result = await self.service.get(f"/currency/{ordinal}/{address}/balance")
        return Balance(**result, meta=result.get("meta"))


class ML1Api(L1Api):
    def __init__(self, host: str):
        super().__init__(host)

    @property
    def service(self) -> RestAPIClient:
        if not self._service:
            raise ValueError("ML1Api :: Metagraph currency layer 1 host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)


class MDL1Api:
    def __init__(self, host: str):
        self._service = RestAPIClient(host) if host else None

    @property
    def service(self) -> RestAPIClient:
        if not self._service:
            raise ValueError("MDL1Api :: Metagraph data layer 1 host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)

    async def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics from the Metagraph data layer 1 endpoint.

        :return: Prometheus output as a list of dictionaries.
        """
        response = await self.service.get("/metrics")
        return _handle_metrics(response)

    async def get_cluster_info(self) -> List[PeerInfo]:
        result = await self.service.get("/cluster/info")
        return PeerInfo.process_cluster_peers(data=result)

    async def get_data(self) -> List[SignedTransaction]:
        """Retrieve enqueued data update objects."""
        # TODO: Implement this method.
        pass

    async def post_data(self, tx: Dict):
        """
        Submit a data update object for processing.

        Example payload:
        {
          "value": {},
          "proofs": [
            {
              "id": "...",
              "signature": "..."
            }
          ]
        }
        """
        return await self.service.post("/data", payload=tx)


