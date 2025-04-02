import json
from typing import Optional, Any, Dict
from httpx import Response
from .di.rest_client import RESTClient, HttpxClient
from pypergraph.core.exceptions import NetworkError


class RestAPIClient:
    def __init__(self, base_url: str, client: Optional[RESTClient] = None, timeout: int = 10):
        """
        Initializes the RestAPIClient.

        :param base_url: The base URL for the API.
        :param client: Optional user-provided AsyncClient.
        :param timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self._external_client = client is not None
        # If no client is provided, use the default HttpxClient.
        self.client: RESTClient = client or HttpxClient(timeout=timeout)


    @property
    def base_url(self) -> str:
        """Returns the base URL."""
        return self._base_url

    @base_url.setter
    def base_url(self, value: str):
        """Updates the base URL."""
        self._base_url = value.rstrip("/")

    def config(self, client: RESTClient):
        self.client = client

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
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = await self.client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            payload=payload
        )
        return self.handle_api_response(response, method, endpoint)

    async def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None,
                  params: Optional[Dict[str, Any]] = None):
        return await self.request("GET", endpoint, headers=headers, params=params)

    async def post(self, endpoint: str, headers: Optional[Dict[str, str]] = None,
                   payload: Optional[Dict[str, Any]] = None):
        return await self.request("POST", endpoint, headers=headers, payload=payload)

    async def put(self, endpoint: str, headers: Optional[Dict[str, str]] = None,
                  payload: Optional[Dict[str, Any]] = None):
        return await self.request("PUT", endpoint, headers=headers, payload=payload)

    async def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None,
                     params: Optional[Dict[str, Any]] = None):
        return await self.request("DELETE", endpoint, headers=headers, params=params)

    async def close(self):
        """
        Closes the HTTPClient session if it was not provided by the user.
        """
        if not self._external_client:
            await self.client.close()

    async def __aenter__(self):
        """Allows usage in async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes client automatically when used in a `with` block."""
        await self.close()

    def handle_api_response(self, response: Response, method: str, endpoint: str):
        """
        Handles API responses, checking for errors and returning JSON or text.
        """
        try:
            parsed_data = response.json()
        except json.JSONDecodeError:
            parsed_data = response.text

        if response.status_code != 200:
            error_detail = parsed_data.get("errors", "Unknown error") if isinstance(parsed_data, dict) else parsed_data
            raise NetworkError(
                f"RestAPIClient :: {method} {self.base_url + endpoint} failed with: {error_detail}",
                status=response.status_code
            )

        if isinstance(parsed_data, dict) and "errors" in parsed_data:
            error_messages = [
                err.get("message", "Unknown error") if isinstance(err, dict) else str(err)
                for err in parsed_data["errors"]
            ]
            raise NetworkError(
                f"RestAPIClient :: {method} {self.base_url + endpoint} returned errors: {error_messages}",
                status=420
            )

        return parsed_data
