from typing import Union, List, Optional, Dict

from pypergraph.core.rest_api_client import RestAPIClient
from pypergraph.network.models import (
    Snapshot,
    BlockExplorerTransaction,
    RewardTransaction,
    Balance,
    CurrencySnapshot,
)
import logging

logger = logging.getLogger(__name__)


class BlockExplorerApi:
    def __init__(self, host: str):
        if not host:
            raise ValueError("BlockExplorerApi :: Block explorer host is not configured.")
        self._host = host

    def config(self, host: str):
        """Reconfigure the RestAPIClient's base URL dynamically."""
        if not host:
            raise ValueError("BlockExplorerApi :: Block explorer host is not configured.")
        self._host = host

    async def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, payload: Optional[Dict] = None
    ) -> Dict:
        """
        Helper function to create a new RestAPIClient instance and make a request.
        """
        async with RestAPIClient(base_url=self._host) as client:
            return await client.request(
                method=method,
                endpoint=endpoint,
                params=params,
                payload=payload,
            )

    async def get_snapshot(self, id: Union[str, int]) -> Snapshot:
        """
        Retrieve a snapshot by its hash or ordinal.

        :param id: Hash or ordinal identifier.
        :return: Snapshot object.
        """
        result = await self._make_request("GET", f"/global-snapshots/{id}")
        return Snapshot(**result["data"])

    async def get_transactions_by_snapshot(self, id: Union[str, int]) -> List[BlockExplorerTransaction]:
        """
        Retrieve transactions for a given snapshot.

        :param id: Hash or ordinal identifier.
        :return: List of BlockExplorerTransaction objects.
        """
        results = await self._make_request("GET", f"/global-snapshots/{id}/transactions")
        return BlockExplorerTransaction.process_transactions(
            data=results["data"],
            meta=results.get("meta"),
        )

    async def get_rewards_by_snapshot(self, id: Union[str, int]) -> List[RewardTransaction]:
        """
        Retrieve reward objects for a given snapshot.

        :param id: Hash or ordinal.
        :return: List of Reward objects.
        """
        results = await self._make_request("GET", f"/global-snapshots/{id}/rewards")
        return RewardTransaction.process_snapshot_rewards(results["data"])

    async def get_latest_snapshot(self) -> Snapshot:
        """
        Get the latest snapshot from the block explorer.

        :return: Snapshot object.
        """
        result = await self._make_request("GET", "/global-snapshots/latest")
        return Snapshot(**result["data"])

    async def get_latest_snapshot_transactions(self) -> List[BlockExplorerTransaction]:
        """
        Retrieve transactions for the latest snapshot.

        :return: List of BlockExplorerTransaction objects.
        """
        results = await self._make_request("GET", "/global-snapshots/latest/transactions")
        return BlockExplorerTransaction.process_transactions(
            data=results.get("data"),
            meta=results.get("meta"),
        )

    async def get_latest_snapshot_rewards(self) -> List[RewardTransaction]:
        results = await self._make_request("GET", "/global-snapshots/latest/rewards")
        return RewardTransaction.process_snapshot_rewards(results["data"])

    @staticmethod
    def _get_transaction_search_path_and_params(
        base_path: str,
        limit: Optional[int],
        search_after: Optional[str],
        sent_only: bool,
        received_only: bool,
        search_before: Optional[str],
    ) -> Dict:
        params = {}
        path = base_path

        if limit or search_after or search_before:
            if limit and limit > 0:
                params["limit"] = limit
            if search_after:
                params["search_after"] = search_after
            elif search_before:
                params["search_before"] = search_before

        if sent_only:
            path += "/sent"
        elif received_only:
            path += "/received"

        return {"path": path, "params": params}

    async def get_transactions(
        self,
        limit: Optional[int],
        search_after: Optional[str] = None,
        search_before: Optional[str] = None,
    ) -> List[BlockExplorerTransaction]:
        """
        Get transactions from the block explorer. Supports pagination.

        :param limit: Maximum number of transactions.
        :param search_after: Pagination parameter.
        :param search_before: Pagination parameter.
        :return: List of BlockExplorerTransaction objects.
        """
        base_path = "/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        results = await self._make_request("GET", request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(
            data=results.get("data"),
            meta=results.get("meta"),
        )

    async def get_transactions_by_address(
        self,
        address: str,
        limit: int = 0,
        search_after: str = "",
        sent_only: bool = False,
        received_only: bool = False,
        search_before: str = "",
    ) -> List[BlockExplorerTransaction]:
        """
        Retrieve transactions for a specific DAG address. Supports pagination.

        :param address: DAG address.
        :param limit: Maximum number of transactions.
        :param search_after: Pagination parameter.
        :param sent_only: Filter for sent transactions.
        :param received_only: Filter for received transactions.
        :param search_before: Pagination parameter.
        :return: List of BlockExplorerTransaction objects.
        """
        base_path = f"/addresses/{address}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, sent_only, received_only, search_before
        )
        results = await self._make_request("GET", request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(
            data=results.get("data"),
            meta=results.get("meta"),
        )

    async def get_transaction(self, hash: str) -> BlockExplorerTransaction:
        """
        Retrieve a transaction by its hash.

        :param hash: Transaction hash.
        :return: BlockExplorerTransaction object.
        """
        result = await self._make_request("GET", f"/transactions/{hash}")
        return BlockExplorerTransaction(**result["data"], meta=result.get("meta"))

    async def get_address_balance(self, hash: str) -> Balance:
        """
        Retrieve the balance for a given address from the block explorer.

        :param hash: Address hash.
        :return: Balance object.
        """
        result = await self._make_request("GET", f"/addresses/{hash}/balance")
        return Balance(**result["data"], meta=result.get("meta"))

    async def get_latest_currency_snapshot(self, metagraph_id: str) -> CurrencySnapshot:
        result = await self._make_request("GET", f"/currency/{metagraph_id}/snapshots/latest")
        return CurrencySnapshot(**result["data"], meta=result.get("meta"))

    async def get_currency_snapshot(self, metagraph_id: str, hash_or_ordinal: str) -> CurrencySnapshot:
        result = await self._make_request("GET", f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}")
        return CurrencySnapshot(**result["data"], meta=result.get("meta"))

    async def get_latest_currency_snapshot_rewards(self, metagraph_id: str) -> List[RewardTransaction]:
        result = await self._make_request("GET", f"/currency/{metagraph_id}/snapshots/latest/rewards")
        return RewardTransaction.process_snapshot_rewards(data=result["data"])

    async def get_currency_snapshot_rewards(self, metagraph_id: str, hash_or_ordinal: str) -> List[RewardTransaction]:
        results = await self._make_request("GET", f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}/rewards")
        return RewardTransaction.process_snapshot_rewards(data=results["data"])

    async def get_currency_address_balance(self, metagraph_id: str, hash: str) -> Balance:
        result = await self._make_request("GET", f"/currency/{metagraph_id}/addresses/{hash}/balance")
        return Balance(**result["data"], meta=result.get("meta"))

    async def get_currency_transaction(self, metagraph_id: str, hash: str) -> BlockExplorerTransaction:
        result = await self._make_request("GET", f"/currency/{metagraph_id}/transactions/{hash}")
        return BlockExplorerTransaction(**result["data"], meta=result.get("meta"))

    async def get_currency_transactions(
        self,
        metagraph_id: str,
        limit: Optional[int],
        search_after: Optional[str] = None,
        search_before: Optional[str] = None,
    ) -> List[BlockExplorerTransaction]:
        base_path = f"/currency/{metagraph_id}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        results = await self._make_request("GET", request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results["data"])

    async def get_currency_transactions_by_address(
        self,
        metagraph_id: str,
        address: str,
        limit: int = 0,
        search_after: str = "",
        sent_only: bool = False,
        received_only: bool = False,
        search_before: str = "",
    ) -> List[BlockExplorerTransaction]:
        base_path = f"/currency/{metagraph_id}/addresses/{address}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, sent_only, received_only, search_before
        )
        results = await self._make_request("GET", request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results["data"])

    async def get_currency_transactions_by_snapshot(
        self,
        metagraph_id: str,
        hash_or_ordinal: str,
        limit: int = 0,
        search_after: str = "",
        search_before: str = "",
    ) -> List[BlockExplorerTransaction]:
        base_path = f"/currency/{metagraph_id}/snapshots/{hash_or_ordinal}/transactions"
        request = self._get_transaction_search_path_and_params(
            base_path, limit, search_after, False, False, search_before
        )
        results = await self._make_request("GET", request["path"], params=request["params"])
        return BlockExplorerTransaction.process_transactions(results["data"])
