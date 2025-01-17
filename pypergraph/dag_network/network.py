import warnings
from http.client import responses

import aiohttp
from typing import Any, Dict

from pypergraph.dag_core.exceptions import NetworkError
from pypergraph.dag_network.models import Balance, LastReference, PostTransactionResponse, PendingTransaction

class Network:

    def __init__(self, network: str = "mainnet", l0_host: str | None = None, l1_host: str | None = None, metagraph_id: str | None = None, l0_load_balancer: str | None = None, l1_load_balancer: str | None = None, block_explorer: str | None = None):

        _validate_network_params(network=network, metagraph_id=metagraph_id, l0_host=l0_host, l1_host=l1_host)

        self.network = network
        # TODO: Should not be hardcoded
        self.l1_lb = l1_load_balancer or f"https://l1-lb-{self.network}.constellationnetwork.io"
        self.l0_lb = l0_load_balancer or f"https://l0-lb-{self.network}.constellationnetwork.io"
        self.be = block_explorer or f"https://be-{network}.constellationnetwork.io"
        self.l0_host = l0_host #or self.l0_lb
        self.l1_host = l1_host #or self.l1_lb
        self.metagraph_id = metagraph_id

    def __repr__(self) -> str:
        return (
            f"Network(network={self.network}, l0_host={self.l0_host}, l1_host={self.l1_host}, metagraph_id={self.metagraph_id}, "
            f"l0_load_balancer={self.l0_lb}, l1_load_balancer={self.l1_lb}, block_explorer={self.be})"
        )

    @staticmethod
    async def handle_response(response: aiohttp.ClientResponse) -> Any:
        """Handle HTTP responses, raising custom exceptions for errors."""
        if response.status == 200:
            return await response.json()
        elif response.status == 404:
            return None
        elif response.status == 400:
            error_details = await response.json()
            for error in error_details.get("errors", []):
                if "InsufficientBalance" in error.get("message", ""):
                    raise NetworkError(f"Network :: Transaction failed due to insufficient funds.", status=response.status)
                elif "TransactionLimited" in error.get("message", ""):
                    raise NetworkError("Network :: Transaction failed due to rate limiting.", status=response.status)
                else:
                    raise NetworkError(f"Network :: Unknown error: {error}", status=response.status)
        elif response.status == 500:
            raise NetworkError(message="Network :: Internal server error, try again.", status=response.status)

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
        endpoint = Balance.get_endpoint(dag_address=dag_address, l0_host=self.l0_host, metagraph_id=metagraph_id)
        url = self.l0_host + endpoint if self.l0_host else self.be + endpoint
        response = await self._fetch("GET", url)
        if not d:
            raise NetworkError(message=f"Network :: Please ensure the wallet 'network' parameter match the host or Metagraph network. The wallet 'network' parameter is currently '{self.network}'.", status=404)
        response = Balance(response=d)
        return response.balance if balance_only else response

    async def get_last_reference(self, address_hash: str) -> LastReference:
        """
        Fetch the last reference for a specific DAG address.

        :param address_hash: DAG address or public key
        :return: Dictionary containing the last reference information.
        """
        endpoint = LastReference.get_endpoint(address=address_hash)
        url = self.l1_host + endpoint if self.l1_host else self.l1_lb + endpoint
        ref = await self._fetch("GET", url)
        if not ref:
            raise NetworkError(message=f"Network :: Could not get last reference.", status=404)
        return LastReference(**ref)

    async def get_pending_transaction(self, transaction_hash: str) -> PendingTransaction | None:
        """
        Fetch details of a pending transaction.

        :param transaction_hash: Transaction hash
        :return: Dictionary containing transaction details.
        """
        endpoint = PendingTransaction.get_endpoint(transaction_hash=transaction_hash)
        url = self.l1_host + endpoint if self.l1_host else self.l1_lb + endpoint
        pending = await self._fetch("GET", url)
        return PendingTransaction(pending) if pending else None

    async def post_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """
        Submit a new transaction.

        :param transaction_data: Dictionary containing transaction details.
        :return: Response from the API if no error is raised
        """
        url = self.l1_host + "/transactions" if self.l1_host else self.l1_lb + "/transactions"
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        response = PostTransactionResponse(**await self._fetch("POST", url, headers=headers, json=transaction_data))
        return response.hash

def _validate_network_params(network, metagraph_id, l0_host, l1_host):
    if network not in {"mainnet", "testnet", "integrationnet"}:
        raise ValueError("Network :: Parameter 'network' must be 'mainnet', 'testnet', or 'integrationnet'.")

    if metagraph_id:
        if not (l0_host and l1_host):
            raise ValueError("'l0_host' and 'l1_host' must both be set if 'metagraph_id' is provided.")
    else:
        if l0_host or l1_host:
            if not l0_host:
                warnings.warn("'l1_host' is set but 'l0_host' and 'metagraph_id' is not.")
            if not l1_host:
                warnings.warn("'l0_host' is set but 'l1_host' and 'metagraph_id' is not.")
            if l0_host and l1_host:
                warnings.warn("Network hosts are set without a 'metagraph_id' parameter.")