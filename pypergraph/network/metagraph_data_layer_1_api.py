from typing import List, Dict, Any

from prometheus_client.parser import text_string_to_metric_families

from pypergraph.core.rest_api_client import RestAPIClient
from pypergraph.network.models import PeerInfo, SignedTransaction


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