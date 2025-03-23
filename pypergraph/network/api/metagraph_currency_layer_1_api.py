from pypergraph.core.rest_api_client import RestAPIClient
from pypergraph.network.api.layer_1_api import L1Api


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