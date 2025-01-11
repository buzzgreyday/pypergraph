import aiohttp
from typing import Any, Dict

from pypergraph.dag_network.constants import LB_URL_TEMPLATE, BLOCK_EXPLORER_URL_TEMPLATE
from pypergraph.dag_network.models import Balance, LastReference, PostTransactionResponse, PendingTransaction


class APIError(Exception):
    """Custom base exception for API-related errors."""
    pass


class TransactionError(APIError):
    """Custom exception for transaction-related errors."""
    def __init__(self, message: str, status: int):
        super().__init__(f"{message} (HTTP {status})")
        self.status = status


class API:

    def __init__(self, network: str = "mainnet", layer: int = 1, host: str | None = None, metagraph_id: str | None = None):
        if network not in (None, "mainnet", "testnet", "integrationnet"):
            raise ValueError(f"API :: Network must be None or 'mainnet' or 'integrationnet' or 'testnet'.")
        elif layer not in (None, 0, 1):
            raise ValueError(f"API :: Not a valid layer, must be 0 or 1 integer.")
        elif metagraph_id and not host:
            raise ValueError(f"API :: The parameter 'host' can't be empty.")
        self.network = network
        self.layer = layer
        self.metagraph_id = metagraph_id # If metagraph_id is set, then assume
        self.host = LB_URL_TEMPLATE.format(layer=self.layer, network=self.network) if not host else host
        self.block_explorer_url = BLOCK_EXPLORER_URL_TEMPLATE.format(network=self.network)

    def __repr__(self) -> str:
        return (
            f"API(network={self.network}, layer={self.layer}, "
            f"host={self.host}, current_block_explorer_url={self.block_explorer_url})"
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

                    raise TransactionError("Insufficient balance for transaction", response.status)

        response.raise_for_status()  # Raise for all other errors

    async def _fetch(self, method: str, url: str, **kwargs) -> Any:
        """Reusable method for making HTTP requests."""
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                return await self.handle_response(response)

    async def get_address_balance(self, dag_address: str, metagraph_id: str | None = None, balance_only: bool = True) -> Balance | float:
        """
        Fetch the balance for a specific DAG address or public key.

        :param metagraph_id: This identifier is the DAG address associated with a metagraph.
        :param dag_address: DAG address or public key.
        :param balance_only: If True, return only the balance as a float. Otherwise, return a Balance object.
        :return: Balance object or balance as a float.
        """
        # TODO: These types of urls/endpoints should ofcourse be set/updated centrally. Also, if metagraph_id is
        #  not None use l0 for GET requests and l1 for POST requests by default, else use host with IP:PORT
        url = f"{self.block_explorer_url}/addresses/{dag_address}/balance" if not metagraph_id \
            else f"{self.block_explorer_url}/currency/{metagraph_id}/addresses/{dag_address}/balance"
        # Looks like the block explorer doesn't handle requests as expected. Also, the PACA metagraph returns
        # the balance from here: http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100/currency/{DAG_ADDRESS}/balance
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

