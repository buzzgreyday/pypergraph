import warnings
from typing import Callable, Optional, Any, Coroutine, Dict

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
            raise NetworkError("RestApi :: You must configure at least the http method and url.")
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
        return self.service.get("/metrics")

    async def get_address_balance(self, address: str) -> Coroutine:
        return self.service.get(f"/dag/{address}/balance")

    async def get_last_reference(self, address) -> Coroutine:
        return self.service.get(f"/transactions/last-reference/{address}")

    async def get_total_supply(self) -> Coroutine:
        return self.service.get('/total-supply')

    async def post_transaction(self, tx: Dict[str, Any]) -> Coroutine:
        return self.service.post("/transactions", tx)

    async def get_pending_transaction(self, tx_hash: str) -> Coroutine:
        return self.service.get(f"/transactions/{tx_hash}")

    async def get_cluster_info(self) -> Coroutine:
        return self.service.get("/cluster/info")


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
        return self.service.get(f"/global-snapshots/{id}")

    async def get_transactions_by_snapshot(self, id: str | int) -> Coroutine:
        return self.service.get(f"/global-snapshots/{id}/transactions")