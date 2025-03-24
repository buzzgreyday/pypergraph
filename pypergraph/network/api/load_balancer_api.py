from typing import List, Dict, Any, Union
from prometheus_client.parser import text_string_to_metric_families

from pypergraph.core.rest_api_client import RestAPIClient
from pypergraph.network.models.account import Balance
from pypergraph.network.models.network import TotalSupply, PeerInfo
from pypergraph.network.models.transaction import PendingTransaction, TransactionReference


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
        if not host:
            raise ValueError("LoadBalancerApi :: Load balancer host is not configured.")
        self._host = host

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL."""
        if not host:
            raise ValueError("LoadBalancerApi :: Load balancer host is not configured.")
        self._host = host

    async def _make_request(
        self, method: str, endpoint: str, params: Dict[str, Any] = None, payload: Dict[str, Any] = None
    ) -> Union[Dict, List, str]:
        """
        Helper function to create a new RestAPIClient instance and make a request.
        """
        async with RestAPIClient(base_url=self._host) as client:
            return await client.request(method=method, endpoint=endpoint, params=params, payload=payload)

    async def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics of a random node (served by the LB).

        :return: Prometheus output as a list of dictionaries.
        """
        response = await self._make_request("GET", "/metrics")
        return _handle_metrics(response)

    async def get_address_balance(self, address: str) -> Balance:
        result = await self._make_request("GET", f"/dag/{address}/balance")
        return Balance(**result, meta=result.get("meta"))

    async def get_last_reference(self, address: str) -> TransactionReference:
        result = await self._make_request("GET", f"/transactions/last-reference/{address}")
        return TransactionReference(**result)

    async def get_total_supply(self) -> TotalSupply:
        result = await self._make_request("GET", "/total-supply")
        return TotalSupply(**result)

    async def post_transaction(self, tx: Dict[str, Any]):
        result = await self._make_request("POST", "/transactions", payload=tx)
        return result

    async def get_pending_transaction(self, tx_hash: str) -> PendingTransaction:
        result = await self._make_request("GET", f"/transactions/{tx_hash}")
        return PendingTransaction(**result)

    async def get_cluster_info(self) -> List[PeerInfo]:
        result = await self._make_request("GET", "/cluster/info")
        return PeerInfo.process_cluster_peers(data=result)
