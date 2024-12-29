import requests
from typing import Optional, Callable, Any, Dict

from .constants import DEFAULT_L1_BASE_URL

class RestApiOptions:
    def __init__(self,
                 base_url: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None,
                 no_auth_header: bool = False,
                 transform_response: Optional[Callable] = None,
                 retry: int = 0):  # Default retries to 0
        self.base_url = base_url or DEFAULT_L1_BASE_URL  # Default base URL
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
        return DEFAULT_L1_BASE_URL

    def get_default_protocol_client(self) -> Callable:
        # Default HTTP client using `requests`
        return self.default_http_client

    def default_http_client(self, params: Dict[str, Any]) -> Any:
        url = params.get("url")
        method = params.get("method")
        body = params.get("body")
        headers = {"Authorization": params.get("authToken")} if params.get("authToken") else {}
        query_params = params.get("queryParams", {})
        #print(f"Sending {method} request to {url}")
        #print(f"Headers: {headers}")
        #print(f"Body: {body}")
        #print(f"Query Params: {query_params}")

        try:
            response = requests.request(method, url, headers=headers, json=body, params=query_params)
            #print("Response status:", response.status_code)
            #print("Response headers:", response.headers)
            #print("Response body:", response.text)  # Raw response body
            response.raise_for_status()

            # Safely handle empty responses
            if response.text.strip():  # If the response is not empty
                return response.json()
            else:
                return {"message": "Empty response from server"}  # Default response for empty body
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