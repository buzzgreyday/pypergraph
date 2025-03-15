from json import JSONDecodeError

import httpx
import json

from typing import Callable, Optional, Any, Dict

from httpx import Response

from pypergraph.core.exceptions import NetworkError


class DI:

    def __init__(self):
        #======================
        #   = HTTP Client =
        #======================
        self.http_client = httpx #IHttpClient;
        self.http_client_base_url = ""

    # Register the platform implementation for http service requests
    def register_http_client(self, client, base_url: str):
        """
        Inject another client and/or base_url.

        :param client:
        :param base_url:
        :return:
        """
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
        self.error_hook_callback: Optional[Callable[[Exception], None]] = None

    def set_base_url(self, base_url: str) -> None:
        self.service_base_url = base_url

    def base_url(self, val: Optional[str] = None):
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
            raise ValueError("RestConfig :: No protocol client has been set, and DI().get_http_client() returned None.")

        return self.service_protocol_client

    def error_hook(self, callback: Optional[Callable[[Exception], None]] = None) -> Any:
        if callback is None:
            return self.error_hook_callback

        self.error_hook_callback = callback
        return self

class RestAPIClient:
    def __init__(self, base_url: str, client = None, timeout=10):
        """
        Initializes the RestAPIClient.

        :param base_url: The base URL for the API.
        :param client: An optional injected HTTPX AsyncClient. If not provided, a new one is created.
        """
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.AsyncClient(timeout=timeout)

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

    def handle_api_response(self, response: Response, method: str, endpoint: str):
        # Attempt to parse the response into JSON or fall back to text
        try:
            parsed_data = response.json()
        except json.JSONDecodeError:
            parsed_data = response.text  # Treat as text if JSON parsing fails

        # Check for HTTP status errors (4xx/5xx)
        if response.status_code != 200:
            error_detail = parsed_data
            # Extract error message from JSON if available
            if isinstance(parsed_data, dict):
                error_detail = parsed_data.get("errors", "Unknown error")
            raise NetworkError(
                f"RestAPIClient :: {method} {self.base_url + endpoint} failed with: {error_detail}",
                status=response.status_code
            )

        # Check for business logic errors (e.g., 200 OK but {"errors": [...]})
        if isinstance(parsed_data, dict) and "errors" in parsed_data:
            errors = parsed_data["errors"]
            error_messages = []
            for error in errors:
                if isinstance(error, dict):
                    error_messages.append(error.get("message", "Unknown error"))
                else:
                    raise NetworkError(
                        f"RestAPIClient :: {method} {self.base_url + endpoint} returned unprocessable error: {error}",
                        status=422
                    )
            if error_messages:
                raise NetworkError(
                    f"RestAPIClient :: {method} {self.base_url + endpoint} returned errors: {error_messages}",
                    status=420
                )

        # Return parsed JSON or raw text
        return parsed_data


    async def request(
            self,
            method: str,
            endpoint: str,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            payload: Optional[Dict[str, Any]] = None,
    ):
        """
        Makes an HTTP request.

        :param method: HTTP method (GET, POST, PUT, DELETE, etc.).
        :param endpoint: The endpoint path (appended to base_url).
        :param headers: Optional headers for the request.
        :param params: Optional query parameters.
        :param payload: Optional JSON payload.
        :return: Response object.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        # TODO: All headers should be string
        #if headers:
        #    headers = {k: str(v) for k, v in headers.items()}
        async with httpx.AsyncClient(timeout=6) as client:
            response = await client.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=payload
            )
        response = self.handle_api_response(response, method, endpoint)
        return response

    async def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> json:
        return await self.request("GET", endpoint, headers=headers, params=params)

    async def post(self, endpoint: str, headers: Optional[Dict[str, str]] = None, payload: Optional[Dict[str, Any]]= None) -> json:
        return await self.request("POST", endpoint, headers=headers, payload=payload)

    async def put(self, endpoint: str, headers: Optional[Dict[str, str]] = None, payload: Optional[Dict[str, Any]] = None) -> json:
        return await self.request("PUT", endpoint, headers=headers, payload=payload)

    async def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> json:
        return await self.request("DELETE", endpoint, headers=headers, params=params)

    async def close(self):
        """Closes the client session."""
        await self.client.aclose()