from typing import List, Dict, Any

from prometheus_client.parser import text_string_to_metric_families

from pypergraph.core.rest_api_client import RestAPIClient
from pypergraph.network.models import Balance, LastReference, TotalSupply, PendingTransaction, PeerInfo


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