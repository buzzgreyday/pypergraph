from pypergraph.network.api.layer_1_api import L1Api


class ML1Api(L1Api):
    def __init__(self, host: str):
        super().__init__(host)
