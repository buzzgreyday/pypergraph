from typing import Optional

from pypergraph.core.cross_platform.di.rest_client import RESTClient
from pypergraph.network.api.layer_1_api import L1Api


class ML1Api(L1Api):
    def __init__(self, host: str, client: Optional[RESTClient] = None):
        super().__init__(host=host, client=client)
