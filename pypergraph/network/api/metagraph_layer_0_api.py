from pypergraph.core.rest_api_client import RestAPIClient
from pypergraph.network.api.layer_0_api import L0Api
from pypergraph.network.models import TotalSupply, Balance


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