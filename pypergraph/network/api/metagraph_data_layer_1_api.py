import logging
from typing import List, Dict, Any, Optional, Union

from prometheus_client.parser import text_string_to_metric_families

from pypergraph.core.cross_platform.di.rest_client import RESTClient, HttpxClient
from pypergraph.core.cross_platform.rest_api_client import RestAPIClient
from pypergraph.network.models.network import PeerInfo
from pypergraph.network.models.transaction import SignedTransaction


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
    def __init__(self, host: str, client: Optional[RESTClient] = None):
        if not host:
            logging.warning("MDL1 :: Metagraph layer 1 data API object not set.")
        self._host = host
        self.client = client or HttpxClient(timeout=10)

    def config(self, host: Optional[str] = None, client: Optional[RESTClient] = None):
        """Reconfigure the RestAPIClient."""
        if host:
            self._host = host
        if client:
            self.client = client

    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None, payload: Dict[str, Any] = None) -> Union[Dict, List, str]:
        """
        Helper function to create a new RestAPIClient instance and make a request.
        """
        async with RestAPIClient(base_url=self._host, client=self.client) as client:
            return await client.request(method=method, endpoint=endpoint, params=params, payload=payload)

    async def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get metrics from the Metagraph data layer 1 endpoint.

        :return: Prometheus output as a list of dictionaries.
        """
        response = await self._make_request("GET", "/metrics")
        return _handle_metrics(response)

    async def get_cluster_info(self) -> List[PeerInfo]:
        result = await self._make_request("GET", "/cluster/info")
        return PeerInfo.process_cluster_peers(data=result)

    async def get_data(self) -> List[SignedTransaction]:
        """Retrieve enqueued data update objects."""
        # TODO: How should this be implemented and used?
        raise NotImplementedError("get_data method not yet implemented")

    async def post_data(self, tx: Dict):
        """
        Submit a data update object for processing.

        :param tx: SignedTransaction object containing data and proofs
        """
        return await self._make_request("POST", "/data", payload=tx)