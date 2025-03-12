from typing import Optional, Any, Dict, List, Union
from prometheus_client.parser import text_string_to_metric_families

from pypergraph.dag_network.models.reward import Reward
from pypergraph.dag_core.rest_api_client import RestAPIClient
from pypergraph.dag_network.models.account import Balance, LastReference
from pypergraph.dag_network.models.transaction import PendingTransaction, BlockExplorerTransaction, SignedTransaction
from pypergraph.dag_network.models.network import TotalSupply, PeerInfo
from pypergraph.dag_network.models.snapshot import Snapshot, GlobalSnapshot, CurrencySnapshot, Ordinal

def _handle_metrics(response):
    metrics = []
    for family in text_string_to_metric_families(response):
        for sample in family.samples:
            metrics.append({
                "name": sample[0],
                "labels": sample[1],
                "value": sample[2],
                "type": family.type
            })
    return metrics

class LoadBalancerApi:
    def __init__(self, host):

        self._service = RestAPIClient(host) if host else None

    @property
    def service(self):
        if not self._service:
            raise ValueError("LoadBalancerApi :: Load balancer host is not configured.")
        return self._service


    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)

    async def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics of a random node (served by the LB).

        :return: Prometheus output as list of dictionaries.
        """
        response = await self.service.get("/metrics")
        return _handle_metrics(response)

    async def get_address_balance(self, address: str) -> Balance:
        result = await self.service.get(f"/dag/{address}/balance")
        return Balance(**result, meta=result["meta"] if hasattr(result, "meta") else None)

    async def get_last_reference(self, address) -> LastReference:
        result = await self.service.get(f"/transactions/last-reference/{address}")
        return LastReference(**result)

    async def get_total_supply(self) -> TotalSupply:
        result = await self.service.get('/total-supply')
        return TotalSupply(**result)

    async def post_transaction(self, tx: Dict[str, Any]):
        result = await self.service.post("/transactions", payload=tx)
        return result

    async def get_pending_transaction(self, tx_hash: str):
        result = await self.service.get(f"/transactions/{tx_hash}")
        return PendingTransaction(**result)

    async def get_cluster_info(self) -> List["PeerInfo"]:
        result = await self.service.get("/cluster/info")
        return PeerInfo.process_cluster_peers(data=result)


class BlockExplorerApi:

    def __init__(self, host):

        self._service = RestAPIClient(host) if host else None

    @property
    def service(self):
        if not self._service:
            raise ValueError("BlockExplorerApi :: Block explorer host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL dynamically."""
        self._service = RestAPIClient(host)

    async def get_snapshot(self, id: Union[str, int]) -> Snapshot:
        """

        :param id: Hash or ordinal can be used as identifier.
        :return: Snapshot object.
        """
        result = await self.service.get(f"/global-snapshots/{id}")
        return Snapshot(**result["data"])

    async def get_transactions_by_snapshot(self, id: Union[str, int]) -> List["BlockExplorerTransaction"]:
        """

        :param id:  Hash or ordinal can be used as identifier.
        :return: List of Block Explorer type transactions.
        """
        # TODO: Add parameters limit, search_after, search_before, next
        results = await self.service.get(f"/global-snapshots/{id}/transactions")
        return BlockExplorerTransaction.process_transactions(results["data"], results["meta"] if hasattr(results, "meta") else None)


    async def get_rewards_by_snapshot(self, id: Union[str, int]) -> List[Reward]:
        """

        :param id: Hash or ordinal.
        :return: List of reward type objects.
        """
        results = await self.service.get(f"/global-snapshots/{id}/rewards")
        return Reward.process_snapshot_rewards(results["data"])

    async def get_latest_snapshot(self) -> Snapshot:
        """
        Get the latest snapshot from block explorer.

        :return: Snapshot object.
        """
        result = await self.service.get("/global-snapshots/latest")
        return Snapshot(**result["data"])

    async def get_latest_snapshot_transactions(self) -> List[BlockExplorerTransaction]:
        # TODO: Add parameters limit, search_after, search_before, next (according to Swagger)
        results = await self.service.get("/global-snapshots/latest/transactions")
        return BlockExplorerTransaction.process_transactions(
            data=results["data"],
            meta=results["meta"] if hasattr(results, "meta") else None)

    async def get_latest_snapshot_rewards(self) -> List[Reward]:
        results = await self.service.get("/global-snapshots/latest/rewards")
        return Reward.process_snapshot_rewards(results["data"])

    @staticmethod
    def _get_transaction_search_path_and_params(
            base_path: str, limit: Optional[int], search_after: Optional[str],
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
            self, limit: Optional[int], search_after: Optional[str] = None,
            search_before: Optional[str] = None
    ) -> List["BlockExplorerTransaction"]:
        """
        Get transactions from block explorer. Supports pagination.

        :param limit: Maximum transaction pagination.
        :param search_after:
        :param search_before:
        :return: List of block explorer type transaction objects.
        """
        base_path = "/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        results = await self.service.get(endpoint=request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results["data"])

    async def get_transactions_by_address(
            self, address: str, limit: int = 0, search_after: str = '',
            sent_only: bool = False, received_only: bool = False, search_before: str = ''
    ) -> List[BlockExplorerTransaction]:
        """
        Get transactions from block explorer per DAG address. Supports pagination.

        :param address: DAG address.
        :param limit: Maximum transaction pagination.
        :param search_after:
        :param sent_only:
        :param received_only:
        :param search_before:
        :return:
        """
        base_path = f"/addresses/{address}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, sent_only, received_only, search_before
        )
        results = await self.service.get(endpoint=request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results)

    async def get_transaction(self, hash: str) -> BlockExplorerTransaction:
        """
        Get the transaction associated with the transaction hash.

        :param hash: Transaction hash.
        :return: Block Explorer type transaction object.
        """
        result = await self.service.get(f"/transactions/{hash}")
        return BlockExplorerTransaction(**result["data"], meta=result["meta"] if hasattr(result, "meta") else None)

    async def get_address_balance(self, hash: str) -> Balance:
        """
        Get address balance from block explorer.

        :param hash: Transactions hash.
        :return: Balance object.
        """
        result = await self.service.get(f"/addresses/{hash}/balance")
        return Balance(**result["data"], meta=result["meta"] if hasattr(result, "meta") else None)

    async def get_latest_currency_snapshot(self, metagraph_id: str) -> CurrencySnapshot:
        result = await self.service.get(f"/currency/{metagraph_id}/snapshots/latest")
        return CurrencySnapshot(**result["data"], meta=result["meta"] if hasattr(result, "meta") else None)

    async def get_currency_snapshot(self, metagraph_id: str, hash_or_ordinal: str) -> CurrencySnapshot:
        result = await self.service.get(f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}")
        return CurrencySnapshot(**result["data"], meta=result["meta"] if hasattr(result, "meta") else None)

    async def get_latest_currency_snapshot_rewards(self, metagraph_id: str) -> List[Reward]:
        result = await self.service.get(f"/currency/{metagraph_id}/snapshots/latest/rewards")
        return Reward.process_snapshot_rewards(data=result["data"])

    async def get_currency_snapshot_rewards(
            self, metagraph_id: str, hash_or_ordinal: str
    ) -> List[Reward]:
        results = await self.service.get(f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}/rewards")
        return Reward.process_snapshot_rewards(data=results["data"])

    async def get_currency_address_balance(self, metagraph_id: str, hash: str) -> Balance:
        result = await self.service.get(f"/currency/{metagraph_id}/addresses/{hash}/balance")
        return Balance(**result["data"], meta=result["meta"] if hasattr(result, "meta") else None)

    async def get_currency_transaction(self, metagraph_id: str, hash: str) -> BlockExplorerTransaction:
        result = await self.service.get(f"/currency/{metagraph_id}/transactions/{hash}")
        return BlockExplorerTransaction(**result["data"], meta=result["meta"] if hasattr(result, "meta") else None)

    async def get_currency_transactions(
            self, metagraph_id: str, limit: Optional[int], search_after: Optional[str] = None,
            search_before: Optional[str] = None
    ) -> List[BlockExplorerTransaction]:
        base_path = f"/currency/{metagraph_id}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        results = await self.service.get(endpoint=request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results["data"])

    async def get_currency_transactions_by_address(
            self, metagraph_id: str, address: str, limit: int = 0, search_after: str = '',
            sent_only: bool = False, received_only: bool = False, search_before: str = ''
    ) -> List[BlockExplorerTransaction]:
        base_path = f"/currency/{metagraph_id}/addresses/{address}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, sent_only, received_only, search_before
        )
        results = await self.service.get(endpoint=request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results["data"])

    async def get_currency_transactions_by_snapshot(
            self, metagraph_id: str, hash_or_ordinal: str, limit: int = 0,
            search_after: str = '', search_before: str = ''
    ) -> List[BlockExplorerTransaction]:
        base_path = f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        results = await self.service.get(endpoint=request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results["data"])


class L0Api:

    def __init__(self, host):
        self._service = RestAPIClient(host) if host else None

    @property
    def service(self):
        if not self._service:
            raise ValueError("L0Api :: Layer 0 host is not configured.")
        return self._service


    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)


    async def get_cluster_info(self):
        result = await self.service.get("/cluster/info")
        return PeerInfo.process_cluster_peers(data=result)

    # Metrics
    async def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics of the L0 URL.

        :return: Prometheus output as list of dictionaries.
        """
        response = await self.service.get("/metrics")
        return _handle_metrics(response)

    # DAG
    async def get_total_supply(self):
        result = await self.service.get("/dag/total-supply")
        return TotalSupply(**result)

    async def get_address_balance(self, address: str) -> Balance:
        result = await self.service.get(f"/dag/{address}/balance")
        return Balance(**result, meta=result["meta"] if hasattr(result, "meta") else None)

    # Global Snapshot
    async def get_latest_snapshot(self) -> GlobalSnapshot:
        result = await self.service.get(
            "/global-snapshots/latest"
        )
        return GlobalSnapshot(**result)

    async def get_latest_snapshot_ordinal(self):
        result = await self.service.get("/global-snapshots/latest/ordinal")
        return Ordinal(**result)

    #async def get_snapshot(self, id: Union[str, int]) -> Snapshot:
    #    result = await self.service.get(
    #                 f"/global-snapshots/{id}"
    #             )
    #    return result

    # State Channels
    async def post_state_channel_snapshot(self, address: str, snapshot: dict):
        # TODO: Validation
        return await self.service.post(
            f"/state-channel/{address}/snapshot",
            payload=snapshot
        )

    # TODO: Estimate fee endpoint

class L1Api:

    def __init__(self, host):
        self._service = RestAPIClient(host) if host else None

    @property
    def service(self):
        if not self._service:
            raise ValueError("L1Api :: Currency layer 1 host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)

    async def get_cluster_info(self) -> List["PeerInfo"]:
        result = await self.service.get("/cluster/info")
        return PeerInfo.process_cluster_peers(data=result)

    # Metrics
    async def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics of the L1 URL.

        :return: Prometheus output as list of dictionaries.
        """
        response = await self.service.get("/metrics")
        return _handle_metrics(response)

    # Transactions
    async def get_last_reference(self, address: str) -> LastReference:
        result = await self.service.get(f"/transactions/last-reference/{address}")
        return LastReference(**result)

    async def get_pending_transaction(self, hash: str) -> PendingTransaction:
        result = await self.service.get(f"/transactions/{hash}")
        return PendingTransaction(**result)

    async def post_transaction(self, tx: SignedTransaction):
        return await self.service.post("/transactions", payload=tx.model_dump())

    # TODO: Estimate fee endpoint

class ML0Api(L0Api):
    def __init__(self, host):
        super().__init__(host)

    @property
    def service(self):
        if not self._service:
            raise ValueError("ML0Api :: Metagraph layer 0 host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)

    # State Channel Token
    async def get_total_supply(self) -> TotalSupply:
        result = await self.service.get("/currency/total-supply")
        return TotalSupply(**result)

    async def get_total_supply_at_ordinal(self, ordinal: int) -> TotalSupply:
        result = await self.service.get(f"/currency/{ordinal}/total-supply")
        return TotalSupply(**result)

    async def get_address_balance(self, address: str) -> Balance:
        result = await self.service.get(f"/currency/{address}/balance")
        return Balance(**result, meta=result["meta"] if hasattr(result, "meta") else None)

    async def get_address_balance_at_ordinal(self, ordinal: int, address: str) -> Balance:
        result = await self.service.get(f"/currency/{ordinal}/{address}/balance")
        return Balance(**result, meta=result["meta"] if hasattr(result, "meta") else None)


class ML1Api(L1Api):
    def __init__(self, host):
        super().__init__(host)

    @property
    def service(self):
        if not self._service:
            raise ValueError("ML1Api :: Metagraph currency layer 1 host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)


class MDL1Api:

    def __init__(self, host):
        self._service = RestAPIClient(host) if host else None

    @property
    def service(self):
        if not self._service:
            raise ValueError("MDL1Api :: Metagraph data layer 1 host is not configured.")
        return self._service

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        self._service = RestAPIClient(host)

    # Metrics
    async def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics of the Metagraph data layer 1 URL.

        :return: Prometheus output as list of dictionaries.
        """
        response = await self.service.get("/metrics")
        return _handle_metrics(response)

    async def get_cluster_info(self) -> List["PeerInfo"]:
        result = await self.service.get("/cluster/info")
        return PeerInfo.process_cluster_peers(data=result)

    async def get_data(self) -> List[SignedTransaction]:
        """Get enqueued data update objects."""
        # TODO
        pass

    async def post_data(self, tx: Dict):
        """
        Offer data update object for processing.
        {
          "value": {},
          "proofs": [
            {
              "id": "c7f9a08bdea7ff5f51c8af16e223a1d751bac9c541125d9aef5658e9b7597aee8cba374119ebe83fb9edd8c0b4654af273f2d052e2d7dd5c6160b6d6c284a17c",
              "signature": "3045022017607e6f32295b0ba73b372e31780bd373322b6342c3d234b77bea46adc78dde022100e6ffe2bca011f4850b7c76d549f6768b88d0f4c09745c6567bbbe45983a28bf1"
            }
          ]
        }
        """
        return await self.service.post("/data", payload=tx)

    # TODO: Estimate fee endpoint

