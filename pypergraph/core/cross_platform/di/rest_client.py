from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from httpx import Response  # or define your own response type if needed

class RESTClient(ABC):
    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """Make an HTTP request and return a response."""
        pass

    @abstractmethod
    async def close(self):
        """Clean up the client (close connections, etc.)."""
        pass

class HttpxClient(RESTClient):
    def __init__(self, timeout: int = 10):
        self.client = httpx.AsyncClient(timeout=timeout)

    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Response:
        return await self.client.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            json=payload
        )

    async def close(self):
        await self.client.aclose()