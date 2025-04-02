from typing import Optional

from pypergraph.core.cross_platform.di.rest_client import RESTClient
from pypergraph.network.api.layer_0_api import L0Api
from pypergraph.network.models.network import TotalSupply
from pypergraph.network.models.account import Balance


class ML0Api(L0Api):
    def __init__(self, host: str, client: Optional[RESTClient] = None):
        super().__init__(host=host, client=client)

    async def get_total_supply(self) -> TotalSupply:
        result = await self._make_request("GET", "/currency/total-supply")
        return TotalSupply(**result)

    async def get_total_supply_at_ordinal(self, ordinal: int) -> TotalSupply:
        result = await self._make_request("GET", f"/currency/{ordinal}/total-supply")
        return TotalSupply(**result)

    async def get_address_balance(self, address: str) -> Balance:
        result = await self._make_request("GET", f"/currency/{address}/balance")
        return Balance(**result, meta=result.get("meta"))

    async def get_address_balance_at_ordinal(self, ordinal: int, address: str) -> Balance:
        result = await self._make_request("GET", f"/currency/{ordinal}/{address}/balance")
        return Balance(**result, meta=result.get("meta"))
