import aiohttp
from typing import Any, Dict

from pypergraph.dag_network.constants import LB_URL_TEMPLATE, BLOCK_EXPLORER_URL_TEMPLATE
from pypergraph.dag_network.models import Balance, LastReference, PostTransactionResponse, PendingTransaction


class APIError(Exception):
    """Custom base exception for API-related errors."""
    pass


class TransactionApiError(APIError):
    """Custom exception for transaction-related errors."""
    def __init__(self, message: str, status: int):
        super().__init__(f"{message} (HTTP {status})")
        self.status = status


class API:

    def __init__(self, network: str = "mainnet", layer: int = 1, host: str | None = None, metagraph_id: str | None = None):
        if network not in (None, "mainnet", "testnet", "integrationnet", "metagraph"):
            raise ValueError(f"API :: Network must be None or 'mainnet' or 'integrationnet' or 'testnet' or 'metagraph")
        elif network == "metagraph" and (not host or not metagraph_id):
            raise ValueError("API :: Parameters 'host' and 'metagraph_id' are required with metagraph.")
        elif layer not in (None, 0, 1):
            raise ValueError(f"API :: Not a valid layer, must be 0 or 1 integer.")
        self.network = network
        self.layer = layer
        self.metagraph_id = metagraph_id
        self.host = LB_URL_TEMPLATE.format(layer=self.layer, network=self.network) if not host else host
        self.block_explorer_url = BLOCK_EXPLORER_URL_TEMPLATE.format(network=self.network)

    def __repr__(self) -> str:
        return (
            f"API(network={self.network}, layer={self.layer}, "
            f"current_base_url={self.host}, current_block_explorer_url={self.block_explorer_url})"
        )

    @staticmethod
    async def handle_response(response: aiohttp.ClientResponse) -> Any:
        """Handle HTTP responses, raising custom exceptions for errors."""
        if response.status == 200:
            return await response.json()
        elif response.status == 404:
            return None

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

    async def get_address_balance(self, address_hash: str, balance_only: bool = True) -> Balance | float:
        """
        Fetch the balance for a specific DAG address or public key.

        :param address_hash: DAG address or public key
        :param balance_only: If True, return only the balance as a float. Otherwise, return a Balance object.
        :return: Balance object or balance as a float.
        """
        url = f"{self.block_explorer_url}/addresses/{address_hash}/balance"
        d = await self._fetch("GET", url)
        data = d.get("data")
        meta = d.get("meta", None)
        response = Balance(data=data, meta=meta)
        return response.balance if balance_only else response

    async def get_last_reference(self, address_hash: str) -> LastReference:
        """
        Fetch the last reference for a specific DAG address.

        :param address_hash: DAG address or public key
        :return: Dictionary containing the last reference information.
        """
        url = f"{self.host}/transactions/last-reference/{address_hash}"
        return LastReference(**await self._fetch("GET", url))

    async def get_pending_transaction(self, transaction_hash: str) -> PendingTransaction | None:
        """
        Fetch details of a pending transaction.

        :param transaction_hash: Transaction hash
        :return: Dictionary containing transaction details.
        """
        url = f"{self.host}/transactions/{transaction_hash}"
        pending = await self._fetch("GET", url)

        return PendingTransaction(pending) if pending else None

    async def post_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """
        Submit a new transaction.

        :param transaction_data: Dictionary containing transaction details.
        :return: Response from the API if no error is raised
        """
        url = f"{self.host}/transactions"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        response = PostTransactionResponse(**await self._fetch("POST", url, headers=headers, json=transaction_data))
        return response.hash

