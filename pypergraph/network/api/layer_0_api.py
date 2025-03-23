from typing import List, Dict, Any

from prometheus_client.parser import text_string_to_metric_families

from pypergraph.core.rest_api_client import RestAPIClient
from pypergraph.network.models import PeerInfo, TotalSupply, Balance, GlobalSnapshot, Ordinal


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