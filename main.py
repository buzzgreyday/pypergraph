# RestApi
from typing import Optional, Callable, Any, Type, Dict
import requests

# dto
from pydantic import BaseModel

from dag_keystore import Bip32, Bip39, Wallet

# dag4.dag-network.src.dto.v2.transactions.ts

class TransactionReference(BaseModel):
    hash: str
    ordinal: int

class TransactionValueV2(BaseModel):
    source: str
    destination: str
    amount: float
    fee: float
    parent: TransactionReference
    salt: int | str

class TransactionV2(BaseModel):
    hash: str
    source: str
    destination: str
    amount: float
    fee: float
    parent: TransactionReference
    snapshot: str
    block: str
    timestamp: str
    transactionOriginal: TransactionReference

class Proof(BaseModel):
    signature: str
    id: str

class PostTransactionV2(BaseModel):
    value: TransactionValueV2
    proofs: Proof

class PostTransactionResponseV2(BaseModel):
    hash: str

class GetTransactionResponseV2(BaseModel):
    data: TransactionV2

BASE_URLS = {
                "BLOCK_EXPLORER_URL": 'https://block-explorer.constellationnetwork.io',
                "LOAD_BALANCER_URL": 'http://lb.constellationnetwork.io:9000',
                "L0_URL": 'https://l0-lb-mainnet.constellationnetwork.io',
                "L1_URL": 'https://l1-lb-mainnet.constellationnetwork.io',
            }

# packages/dag4-core/src/cross-platform/api/rest.api.ts

class RestApiOptions:
    def __init__(self,
                 base_url: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None,
                 no_auth_header: bool = False,
                 transform_response: Optional[Callable] = None,
                 retry: int = 0):  # Default retries to 0
        self.base_url = base_url or 'https://l1-lb-mainnet.constellationnetwork.io'  # Default base URL
        self.headers = headers or {}
        self.no_auth_header = no_auth_header
        self.transform_response = transform_response
        self.retry = retry

class RestApiOptionsRequest(RestApiOptions):
    def __init__(self, method: str, body: Any, url: str, error_hook: Optional[Callable] = None,
                 query_params: Optional[Dict[str, Any]] = None, auth_token: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.method = method
        self.body = body
        self.url = url
        self.error_hook = error_hook
        self.query_params = query_params
        self.auth_token = auth_token

class RestConfig:
    def __init__(self):
        self._base_url = None
        self._auth_token = None
        self._protocol_client = None
        self._error_hook = None

    def base_url(self, val: Optional[str] = None) -> Optional[str]:
        if val is None:
            return self._base_url or self.get_default_base_url()
        self._base_url = val
        return self

    def auth_token(self, val: Optional[str] = None) -> Optional[str]:
        if val is None:
            return self._auth_token
        self._auth_token = val
        return self

    def protocol_client(self, val: Optional[Callable] = None) -> Callable:
        if val is None:
            return self._protocol_client or self.get_default_protocol_client()
        self._protocol_client = val
        return self

    def error_hook(self, callback: Optional[Callable[[Any], None]] = None) -> Optional[Callable[[Any], None]]:
        if callback is None:
            return self._error_hook
        self._error_hook = callback
        return self

    def get_default_base_url(self) -> str:
        # Replace with your application's default base URL
        return 'https://l1-lb-mainnet.constellationnetwork.io'

    def get_default_protocol_client(self) -> Callable:
        # Default HTTP client using `requests`
        return self.default_http_client

    def default_http_client(self, params: Dict[str, Any]) -> Any:
        url = params.get("url")
        method = params.get("method")
        body = params.get("body")
        headers = {"Authorization": params.get("authToken")} if params.get("authToken") else {}
        query_params = params.get("queryParams", {})

        try:
            response = requests.request(method, url, headers=headers, json=body, params=query_params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if self._error_hook:
                self._error_hook(e)
            else:
                raise e

class RestApi:
    def __init__(self, base_url: str):
        self.config = RestConfig()
        self.config.base_url(base_url)

    def http_request(self, url: str, method: str, data: Any, options: Optional[RestApiOptions] = None,
                     query_params: Optional[Dict[str, Any]] = None):
        if options is None:
            options = RestApiOptions()  # Use a default options object
        client = self.config.protocol_client()
        if client is None:
            raise ValueError("Protocol client is not configured")

        return client({
            "authToken": self.config.auth_token(),
            "url": self.resolve_url(url, options),  # Use resolve_url to handle options.base_url
            "body": data,
            "method": method,
            "queryParams": query_params,
            "errorHook": self.config.error_hook(),
            **options.__dict__,  # Pass all options as part of the request
        })

    def configure(self) -> RestConfig:
        return self.config

    def resolve_url(self, url: str, options: Optional[RestApiOptions] = None) -> str:
        if options and options.base_url:
            return options.base_url.rstrip('/') + '/' + url.lstrip('/')
        return self.config.base_url().rstrip('/') + '/' + url.lstrip('/')

    def post(self, url: str, data: Optional[Any] = None, options: Optional[RestApiOptions] = None,
             query_params: Optional[Dict[str, Any]] = None) -> Any:
        return self.http_request(url, 'POST', data, options, query_params)

    def get(self, url: str, query_params: Optional[Dict[str, Any]] = None,
            options: Optional[RestApiOptions] = None) -> Any:
        return self.http_request(url, 'GET', None, options, query_params)

    def put(self, url: str, data: Optional[Any] = None, options: Optional[RestApiOptions] = None,
            query_params: Optional[Dict[str, Any]] = None) -> Any:
        return self.http_request(url, 'PUT', data, options, query_params)

    def delete(self, url: str, data: Optional[Any] = None, options: Optional[RestApiOptions] = None,
               query_params: Optional[Dict[str, Any]] = None) -> Any:
        return self.http_request(url, 'DELETE', data, options, query_params)


class Api:
    def __init__(self, base_url: str):
        """
        Initialize with a single base URL, instead of a dictionary of base URLs.
        """
        self.service = RestApi(base_url)  # Use a single service instead of a dictionary of services
        self.current_service_key = base_url  # Only one service is used
        self.config = self.service.config  # Direct access to the configuration

    # dag4.dag-network.src.api.v2.l1-api.ts
    def get_address_last_accepted_transaction_ref(self, address) -> TransactionReference:
        """
        Fetch the transaction reference and parse it into a TransactionReference object.
        """
        endpoint = f"/transactions/last-reference/{address}"
        response_data = self.service.get(endpoint)  # Directly use the service instance
        print(response_data)
        return TransactionReference(**response_data)  # Parse the response into a TransactionReference

def main():
    """Create wallet and test: This is done"""
    bip39 = Bip39()
    bip32 = Bip32()
    wallet = Wallet()
    mnemonic_values = bip39.mnemonic()
    private_key = bip32.get_private_key_from_seed(seed_bytes=mnemonic_values["seed"])
    public_key = bip32.get_public_key_from_private_hex(private_key_hex=private_key)
    dag_addr = wallet.get_dag_address_from_public_key_hex(public_key_hex=public_key)
    print("Values:", mnemonic_values, "\nPrivate Key: " + private_key, "\nPublic Key: " + public_key, "\nDAG Address: " + dag_addr)
    derived_seed = bip39.get_seed_from_mnemonic(words=mnemonic_values["words"])
    derived_private_key = bip32.get_private_key_from_seed(seed_bytes=derived_seed)
    derived_public_key = bip32.get_public_key_from_private_hex(private_key_hex=derived_private_key)
    derived_dag_addr = wallet.get_dag_address_from_public_key_hex(public_key_hex=derived_public_key)
    print(derived_dag_addr, derived_private_key, derived_public_key, derived_seed)

    """Get last reference"""
    try:
        api = Api(BASE_URLS["L1_URL"])  # Pass a single URL instead of the whole dictionary
        transaction_ref = api.get_address_last_accepted_transaction_ref(derived_dag_addr)
        print(transaction_ref)
    except requests.HTTPError as e:
        print(f"HTTP error occurred with main service: {e}")
    except ValueError as ve:
        print(f"Validation error occurred: {ve}")

if __name__ == "__main__":
    main()



