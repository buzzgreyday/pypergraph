import aiohttp


class TransactionApiError(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.error = error_code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (status code: {self.error})"


import aiohttp
from typing import Any, Dict


class APIError(Exception):
    """Custom base exception for API-related errors."""
    pass


class TransactionApiError(APIError):
    """Custom exception for transaction-related errors."""
    def __init__(self, message: str, status: int):
        super().__init__(f"{message} (HTTP {status})")
        self.status = status


class API:
    BASE_URL_TEMPLATE = "https://l{layer}-lb-{network}.constellationnetwork.io"
    BLOCK_EXPLORER_URL_TEMPLATE = "https://be-{network}.constellationnetwork.io"

    def __init__(self, network: str = "mainnet", layer: int = 1):
        self.network = network
        self.layer = layer
        self.current_base_url = self.BASE_URL_TEMPLATE.format(layer=self.layer, network=self.network)
        self.current_block_explorer_url = self.BLOCK_EXPLORER_URL_TEMPLATE.format(network=self.network)

    def __repr__(self) -> str:
        return (
            f"API(network={self.network}, layer={self.layer}, "
            f"current_base_url={self.current_base_url}, current_block_explorer_url={self.current_block_explorer_url})"
        )

    @staticmethod
    async def handle_response(response: aiohttp.ClientResponse) -> Any:
        """Handle HTTP responses, raising custom exceptions for errors."""
        if response.status == 200:
            return await response.json()

        response_data = await response.json()
        if response.status == 400:
            for error in response_data.get("errors", []):
                if "InsufficientBalance" in error.get("message", ""):
                    message = error["message"]
                    amount_str = message.split("amount=")[1].split(",")[0]
                    balance_str = message.split("balance=")[1].strip("}")
                    amount = int(amount_str)  # Example: parse or log
                    balance = int(balance_str)  # Example: parse or log

                    raise TransactionApiError("Insufficient balance for transaction", response.status)

        response.raise_for_status()  # Raise for all other errors

    async def _fetch(self, method: str, url: str, **kwargs) -> Any:
        """Reusable method for making HTTP requests."""
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                return await self.handle_response(response)

    async def get_address_balance(self, address_hash: str) -> Dict[str, Any]:
        """
        Fetch the balance for a specific DAG address or public key.
        :param address_hash: DAG address or public key
        :return: Dictionary containing the balance information.
        """
        url = f"{self.current_block_explorer_url}/addresses/{address_hash}/balance"
        return await self._fetch("GET", url)

    async def get_last_reference(self, address_hash: str) -> Dict[str, Any]:
        """
        Fetch the last reference for a specific DAG address.
        :param address_hash: DAG address or public key
        :return: Dictionary containing the last reference information.
        """
        url = f"{self.current_base_url}/transactions/last-reference/{address_hash}"
        return await self._fetch("GET", url)

    async def get_pending_transaction(self, transaction_hash: str) -> Dict[str, Any]:
        """
        Fetch details of a pending transaction.
        :param transaction_hash: Transaction hash
        :return: Dictionary containing transaction details.
        """
        url = f"{self.current_base_url}/transactions/{transaction_hash}"
        return await self._fetch("GET", url)

    async def post_transaction(self, transaction_data: Dict[str, Any]) -> None:
        """
        Submit a new transaction.
        :param transaction_data: Dictionary containing transaction details.
        """
        url = f"{self.current_base_url}/transactions"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        await self._fetch("POST", url, headers=headers, json=transaction_data)

