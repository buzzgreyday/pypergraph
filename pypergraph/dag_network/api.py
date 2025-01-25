import warnings
from datetime import datetime
from typing import Callable, Optional, Any, Coroutine, Dict, List

from pypergraph.dag_core.exceptions import NetworkError


class DI:

    def __init__(self):
        #======================
        #   = HTTP Client =
        #======================
        self.http_client = None #IHttpClient;
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

    def protocol_client(self, val = None):
        if not val:
            return self.service_protocol_client or DI().get_http_client()

        self.service_protocol_client = val
        return self

    def error_hook(self, callback: Optional[Callable[[Exception], None]] = None) -> Any:
        if callback is None:
            return self.error_hook_callback

        self.error_hook_callback = callback
        return self

class RestApi:

    def __init__(self, base_url):
        self.config = RestConfig()
        self.base_url: str = self.config.base_url(base_url)

    def http_request(self, url: str, method: str, data: Any, options: dict, query_params: Any):
        url = self.resolve_url(url, options)
        if not method or not url:
            raise ValueError("RestApi :: You must configure at least the http method and url.")
        client = self.config.protocol_client()
        return client.invoke({
                    "auth_token": self.config.auth_token(),
                    "url": url,
                    "body": data,
                    "method": method,
                    "query_params": query_params,
                    "error_hook": self.config.error_hook(),
                    **options,
                })

    def configure(self) -> RestConfig:
        return self.config

    def resolve_url(self, url, options: dict):
        if options and options["base_url"] != "":
            url = options["base_url"] + url
        else:
            url = self.config.base_url() + url
        return url

    async def post(self, url: str, data=None, options=None, query_params=None):
        return await self.http_request(url, "POST", data, options, query_params)

    async def get(self, url: str, query_params=None, options=None):
        return await self.http_request(url, "GET", None, options, query_params)

    async def put(self, url: str, data=None, options=None, query_params=None):
        return await self.http_request(url, "PUT", data, options, query_params)

    async def delete(self, url: str, data=None, options=None, query_params=None):
        return await self.http_request(url, "DELETE", data, options, query_params)

class LoadBalancerApi:
    # TODO: Data cleaning and validation
    def __init__(self, host):
        """Data validation and cleaning is needed"""
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"LoadBalancerApi :: Invalid host: {host}")
        self.service = RestApi(host)
        self.host = self.config().base_url(host)

    def config(self):
        return self.service.configure()

    async def get_metrics(self) -> Coroutine:
        result = await self.service.get("/metrics")
        return result

    async def get_address_balance(self, address: str) -> Coroutine:
        result = await self.service.get(f"/dag/{address}/balance")
        return result

    async def get_last_reference(self, address) -> Coroutine:
        result = await self.service.get(f"/transactions/last-reference/{address}")
        return result

    async def get_total_supply(self) -> Coroutine:
        result = await self.service.get('/total-supply')
        return result

    async def post_transaction(self, tx: Dict[str, Any]) -> Coroutine:
        result = await self.service.post("/transactions", tx)
        return result

    async def get_pending_transaction(self, tx_hash: str) -> Coroutine:
        result = await self.service.get(f"/transactions/{tx_hash}")
        return result

    async def get_cluster_info(self) -> Coroutine:
        result = await self.service.get("/cluster/info")
        return result


class BlockExplorerApi:

    def __init__(self, host):
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"BlockExplorerApi :: Invalid host: {host}")
        self.service = RestApi(host)
        self.host = self.config().base_url(host)

    def config(self):
        return self.service.configure()

    async def get_snapshot(self, id: str | int) -> Coroutine:
        result = await self.service.get(f"/global-snapshots/{id}")
        return result

    async def get_transactions_by_snapshot(self, id: str | int) -> Coroutine:
        result = await self.service.get(f"/global-snapshots/{id}/transactions")
        return result

    async def get_rewards_by_snapshot(self, id: str | int) -> Coroutine:
        result = await self.service.get(f"/global-snapshots/{id}/rewards")
        return result

    async def get_latest_snapshot(self) -> Coroutine:
        result = await self.service.get("/global-snapshots/latest")
        return result

    async def get_latest_snapshot_transaction(self) -> Coroutine:
        result = await self.service.get("/global-snapshots/latest/transactions")
        return result

    async def get_latest_snapshot_rewards(self) -> Coroutine:
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
        self.service = RestApi(host)
        self.host = self.config().base_url(host)

    def config(self):
        return self.service.configure()

    async def get_cluster_info(self) -> Coroutine:
        result = await self.service.get("/cluster/info")
        return result

    # Metrics
    async def get_metrics(self) -> Coroutine:
        # TODO: Data clean up - parsing
        return await self.service.get("/metrics")

    # DAG
    async def get_total_supply(self) -> Coroutine:
        return await self.service.get("/dag/total-supply")

    async def get_total_supply_at_ordinal(self, ordinal: int) -> Coroutine:
        return await self.service.get(f"/dag/{ordinal}/total-supply")

    async def get_address_balance(self, address: str) -> Coroutine:
        return await self.service.get(f"/dag/{address}/balance")

    async def get_address_balance_at_ordinal(self, ordinal: int, address: str) -> Coroutine:
        return await self.service.get(f"/dag/{ordinal}/{address}/balance")

    # Global Snapshot
    async def get_latest_snapshot(self) -> Coroutine:
        return await self.service.get(
            "/global-snapshots/latest",
            options={"headers": {"Accept": "application/json"}}
        )

    async def get_latest_snapshot_ordinal(self) -> Coroutine:
        return await self.service.get("/global-snapshots/latest/ordinal")

    async def get_snapshot(self, id: str | int) -> Coroutine:
        return await self.service.get(
            f"/global-snapshots/{id}",
            options={"headers": {"Accept": "application/json"}}
        )

    # State Channels
    async def post_state_channel_snapshot(self, address: str, snapshot: str) -> Coroutine:
        return await self.service.post(
            f"/state-channel/{address}/snapshot",
            snapshot
        )

class L1Api:

    def __init__(self, host):
        if not host.startswith("http"):
            warnings.warn("Adding default prefix 'http://' since 'host' param is missing 'http://' or 'https:// prefix.")
            host = f"http://{host}"
        if not host or type(host) != str:
            raise ValueError(f"L0Api :: Invalid host: {host}")
        self.service = RestApi(host)
        self.host = self.config().base_url(host)

    def config(self):
        return self.service.configure()

    async def get_cluster_info(self) -> Coroutine:
        result = await self.service.get("/cluster/info")
        return result

    # Metrics
    async def get_metrics(self) -> Coroutine:
        # TODO: add parsing for v2 response... returns 404
        return await self.service.get("/metric")

    # Transactions
    async def get_last_reference(self, address: str) -> Coroutine:
        return await self.service.get(f"/transactions/last-reference/{address}")

    async def get_pending_transaction(self, hash: str) -> Coroutine:
        return await self.service.get(f"/transactions/{hash}")

    async def post_transaction(self, tx) -> Coroutine:
        return await self.service.post("/transactions", tx)

class ML0Api(L0Api):
    def __init__(self, host):
        super().__init__(host)

    # State Channel Token
    async def get_total_supply(self) -> Coroutine:
        return await self.service.get("/currency/total-supply")

    async def get_total_supply_at_ordinal(self, ordinal: int) -> Coroutine:
        return await self.service.get(f"/currency/{ordinal}/total-supply")

    async def get_address_balance(self, address: str) -> Coroutine:
        return await self.service.get(f"/currency/{address}/balance")

    async def get_address_balance_at_ordinal(self, ordinal: int, address: str) -> Coroutine:
        return await self.service.get(f"/currency/{ordinal}/{address}/balance")


class ML1Api(L1Api):
    def __init__(self, host):
        super().__init__(host)

