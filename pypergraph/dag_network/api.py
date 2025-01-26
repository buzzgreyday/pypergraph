import warnings
from datetime import datetime
from decimal import Decimal
from typing import Callable, Optional, Any, Coroutine, Dict, List

import httpx

from pypergraph.dag_network.client import FetchRestService


class DI:

    def __init__(self):
        #======================
        #   = HTTP Client =
        #======================
        self.http_client = httpx #IHttpClient;
        self.http_client_base_url = ""

    # Register the platform implementation for http service requests
    def register_http_client(self, client, base_url: str):
        self.http_client = client
        self.http_client_base_url = base_url or ''


    def get_http_client(self): # IHttpClient {
        return self.http_client

    def get_http_client_base_url(self) -> str:
        return self.http_client_base_url


class RestConfig:
    def __init__(self):
        self.service_base_url = None
        self.service_auth_token: str = ""
        self.service_protocol_client = None
        self.error_hook_callback: Callable[[Exception], None] | None = None

    def set_base_url(self, base_url: str) -> None:
        self.service_base_url = base_url

    def base_url(self, val: str | None = None):
        if not val:
            return "" if self.service_base_url == "" else self.service_base_url or DI().get_http_client_base_url()

    def auth_token(self, val: str = None):
        if not val:
            return self.service_auth_token

        self.service_auth_token = val

        return self

    def protocol_client(self, val=None):
        if val is not None:
            self.service_protocol_client = val
            return self

        if self.service_protocol_client is None:
            self.service_protocol_client = DI().get_http_client()

        if self.service_protocol_client is None:
            raise ValueError("No protocol client has been set, and DI().get_http_client() returned None.")

        return self.service_protocol_client

    def error_hook(self, callback: Optional[Callable[[Exception], None]] = None) -> Any:
        if callback is None:
            return self.error_hook_callback

        self.error_hook_callback = callback
        return self

class RestAPIClient:
    def __init__(self, base_url: str, client: Optional[httpx.AsyncClient] = None):
        """
        Initializes the RestAPIClient.

        :param base_url: The base URL for the API.
        :param client: An optional injected HTTPX AsyncClient. If not provided, a new one is created.
        """
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.AsyncClient()

    @property
    def base_url(self) -> str:
        """Returns the current base URL."""
        return self._base_url

    @base_url.setter
    def base_url(self, value: str):
        """
        Updates the base URL.

        :param value: The new base URL.
        """
        self._base_url = value.rstrip("/")
        print(f"Base URL updated to: {self._base_url}")

    async def request(
            self,
            method: str,
            endpoint: str,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """
        Makes an HTTP request.

        :param method: HTTP method (GET, POST, PUT, DELETE, etc.).
        :param endpoint: The endpoint path (appended to base_url).
        :param headers: Optional headers for the request.
        :param params: Optional query parameters.
        :param json: Optional JSON payload.
        :return: HTTPX Response object.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        # TODO: All headers should be string
        if headers:
            headers = {k: str(v) for k, v in headers.items()}
        response = await self.client.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            json=json,
        )
        response.raise_for_status()
        return response.json()

    async def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        print(headers)
        return await self.request("GET", endpoint, headers=headers, params=params)

    async def post(self, endpoint: str, headers: Optional[Dict[str, str]] = None, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        # TODO: serialize json
        print(headers, json)
        return await self.request("POST", endpoint, headers=headers, json=json)

    async def put(self, endpoint: str, headers: Optional[Dict[str, str]] = None, json: Optional[Dict[str, Any]] = None) -> httpx.Response:
        print(headers, json)
        return await self.request("PUT", endpoint, headers=headers, json=json)

    async def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        print(headers)
        return await self.request("DELETE", endpoint, headers=headers, params=params)

    async def close(self):
        """Closes the client session."""
        await self.client.aclose()

class LoadBalancerApi:
    # TODO: Data cleaning and validation
    def __init__(self, host):
        """Data validation and cleaning is needed"""
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"LoadBalancerApi :: Invalid host: {host}")
        self.service = RestAPIClient(host)

    async def get_metrics(self):
        result = await self.service.get("/metrics")
        return result

    async def get_address_balance(self, address: str):
        result = await self.service.get(f"/dag/{address}/balance")
        return result

    async def get_last_reference(self, address):
        result = await self.service.get(f"/transactions/last-reference/{address}")
        return result

    async def get_total_supply(self):
        result = await self.service.get('/total-supply')
        return result

    async def post_transaction(self, tx: Dict[str, Any]):
        result = await self.service.post("/transactions", json=tx)
        return result

    async def get_pending_transaction(self, tx_hash: str):
        result = await self.service.get(f"/transactions/{tx_hash}")
        return result

    async def get_cluster_info(self):
        result = await self.service.get("/cluster/info")
        return result


class BlockExplorerApi:

    def __init__(self, host):
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"BlockExplorerApi :: Invalid host: {host}")
        self.service = RestAPIClient(host)

    async def get_snapshot(self, id: str | int):
        result = await self.service.get(f"/global-snapshots/{id}")
        return result

    async def get_transactions_by_snapshot(self, id: str | int):
        result = await self.service.get(f"/global-snapshots/{id}/transactions")
        return result

    async def get_rewards_by_snapshot(self, id: str | int):
        result = await self.service.get(f"/global-snapshots/{id}/rewards")
        return result

    async def get_latest_snapshot(self):
        result = await self.service.get("/global-snapshots/latest")
        return result

    async def get_latest_snapshot_transaction(self):
        result = await self.service.get("/global-snapshots/latest/transactions")
        return result

    async def get_latest_snapshot_rewards(self):
        result = await self.service.get("/global-snapshots/latest/rewards")
        return result

    def _format_date(self, date: datetime, param_name: str) -> str:
        try:
            return date.isoformat()
        except Exception:
            raise ValueError(f'ParamError: "{param_name}" is not valid ISO 8601')

    def _get_transaction_search_path_and_params(
            self, base_path: str, limit: Optional[int], search_after: Optional[str],
            sent_only: bool, received_only: bool, search_before: Optional[str]
    ) -> Dict:
        params = {}
        path = base_path

        if limit or search_after or search_before:
            if limit and limit > 0:
                params["limit"] = limit
            if search_after:
                params["search_after"] = search_after
            elif search_before:
                params["search_before"] = search_before

        if sent_only:
            path += '/sent'
        elif received_only:
            path += '/received'

        return {"path": path, "params": params}

    async def get_transactions(
            self, limit: Optional[int], search_after: Optional[str],
            search_before: Optional[str]
    ) -> List[Dict]:
        base_path = "/transactions"
        result = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        return await self.service.get(result["path"], result["params"])

    async def get_transactions_by_address(
            self, address: str, limit: int = 0, search_after: str = '',
            sent_only: bool = False, received_only: bool = False, search_before: str = ''
    ) -> List[Dict]:
        base_path = f"/addresses/{address}/transactions"
        result = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, sent_only, received_only, search_before
        )
        return await self.service.get(result["path"], result["params"])

    async def get_transaction(self, hash: str) -> Dict:
        return await self.service.get(f"/transactions/{hash}")

    async def get_address_balance(self, hash: str) -> Dict:
        return await self.service.get(f"/addresses/{hash}/balance")

    async def get_checkpoint_block(self, hash: str) -> Dict:
        return await self.service.get(f"/blocks/{hash}")

    async def get_latest_currency_snapshot(self, metagraph_id: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/snapshots/latest")

    async def get_currency_snapshot(self, metagraph_id: str, hash_or_ordinal: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}")

    async def get_latest_currency_snapshot_rewards(self, metagraph_id: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/snapshots/latest/rewards")

    async def get_currency_snapshot_rewards(
            self, metagraph_id: str, hash_or_ordinal: str
    ) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}/rewards")

    async def get_currency_block(self, metagraph_id: str, hash: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/blocks/{hash}")

    async def get_currency_address_balance(self, metagraph_id: str, hash: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/addresses/{hash}/balance")

    async def get_currency_transaction(self, metagraph_id: str, hash: str) -> Dict:
        return await self.service.get(f"/currency/{metagraph_id}/transactions/{hash}")

    async def get_currency_transactions(
            self, metagraph_id: str, limit: Optional[int], search_after: Optional[str],
            search_before: Optional[str]
    ) -> List[Dict]:
        base_path = f"/currency/{metagraph_id}/transactions"
        result = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        return await self.service.get(result["path"], result["params"])

    async def get_currency_transactions_by_address(
            self, metagraph_id: str, address: str, limit: int = 0, search_after: str = '',
            sent_only: bool = False, received_only: bool = False, search_before: str = ''
    ) -> List[Dict]:
        base_path = f"/currency/{metagraph_id}/addresses/{address}/transactions"
        result = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, sent_only, received_only, search_before
        )
        return await self.service.get(result["path"], result["params"])

    async def get_currency_transactions_by_snapshot(
            self, metagraph_id: str, hash_or_ordinal: str, limit: int = 0,
            search_after: str = '', search_before: str = ''
    ) -> List[Dict]:
        base_path = f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}/transactions"
        result = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        return await self.service.get(result["path"], result["params"])


class L0Api:

    def __init__(self, host):
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"L0Api :: Invalid host: {host}")
        self.service = RestAPIClient(host)

    async def get_cluster_info(self):
        result = await self.service.get("/cluster/info")
        return result

    # Metrics
    async def get_metrics(self):
        # TODO: Data clean up - parsing
        return await self.service.get("/metrics")

    # DAG
    async def get_total_supply(self):
        return await self.service.get("/dag/total-supply")

    async def get_total_supply_at_ordinal(self, ordinal: int):
        return await self.service.get(f"/dag/{ordinal}/total-supply")

    async def get_address_balance(self, address: str):
        return await self.service.get(f"/dag/{address}/balance")

    async def get_address_balance_at_ordinal(self, ordinal: int, address: str):
        return await self.service.get(f"/dag/{ordinal}/{address}/balance")

    # Global Snapshot
    async def get_latest_snapshot(self):
        return await self.service.get(
            "/global-snapshots/latest",
            options={"headers": {"Accept": "application/json"}}
        )

    async def get_latest_snapshot_ordinal(self):
        return await self.service.get("/global-snapshots/latest/ordinal")

    async def get_snapshot(self, id: str | int):
        return await self.service.get(
            f"/global-snapshots/{id}",
            options={"headers": {"Accept": "application/json"}}
        )

    # State Channels
    async def post_state_channel_snapshot(self, address: str, snapshot: str):
        return await self.service.post(
            f"/state-channel/{address}/snapshot",
            json=snapshot
        )

class L1Api:

    def __init__(self, host):
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"L0Api :: Invalid host: {host}")
        self.service = RestAPIClient(host)

    async def get_cluster_info(self):
        result = await self.service.get("/cluster/info")
        return result

    # Metrics
    async def get_metrics(self):
        # TODO: add parsing for v2 response... returns 404
        return await self.service.get("/metric")

    # Transactions
    async def get_last_reference(self, address: str):
        return await self.service.get(f"/transactions/last-reference/{address}")

    async def get_pending_transaction(self, hash: str):
        return await self.service.get(f"/transactions/{hash}")

    async def post_transaction(self, tx):
        return await self.service.post("/transactions", json=tx)

class ML0Api(L0Api):
    def __init__(self, host):
        super().__init__(host)

    # State Channel Token
    async def get_total_supply(self):
        return await self.service.get("/currency/total-supply")

    async def get_total_supply_at_ordinal(self, ordinal: int):
        return await self.service.get(f"/currency/{ordinal}/total-supply")

    async def get_address_balance(self, address: str):
        return await self.service.get(f"/currency/{address}/balance")

    async def get_address_balance_at_ordinal(self, ordinal: int, address: str):
        return await self.service.get(f"/currency/{ordinal}/{address}/balance")


class ML1Api(L1Api):
    def __init__(self, host):
        super().__init__(host)

