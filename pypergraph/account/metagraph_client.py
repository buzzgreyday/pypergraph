import asyncio
from datetime import datetime

from typing import Any, Dict, List, Optional, Union

from pypergraph.network.shared.operations import allow_spend, token_lock
from pypergraph.network.models.transaction import (
    SignedTransaction,
    TransactionReference,
)
from pypergraph.network.metagraph_network import MetagraphTokenNetwork


class MetagraphTokenClient:
    """
    Create a metagraph account from DagAccount.
    """

    from pypergraph.account import DagAccount

    def __init__(
        self,
        account: DagAccount,
        metagraph_id: str,
        block_explorer_url: Optional[str] = None,
        l0_host: Optional[str] = None,
        currency_l1_host: Optional[str] = None,
        data_l1_host: Optional[str] = None,
        token_decimals: int = 8,
    ):
        self.account = account
        self.network = MetagraphTokenNetwork(
            metagraph_id=metagraph_id,
            l0_host=l0_host,
            currency_l1_host=currency_l1_host,
            data_l1_host=data_l1_host,
            network_id=account.network.connected_network.network_id,
            block_explorer=block_explorer_url or account.network.be_api._host,
        )
        self.token_decimals = token_decimals

    @property
    def network_instance(self):
        return self.network

    @property
    def address(self):
        return self.account.address

    async def get_transactions(
        self, limit: Optional[int] = None, search_after: Optional[str] = None
    ):
        """
        Get paginated list of Block Explorer transaction objects.

        :param limit: Limit per page.
        :param search_after: Timestamp.
        :return:
        """
        return await self.network.get_transactions_by_address(
            self.address, limit, search_after
        )

    async def get_balance(self) -> int:
        """
        Get Metagraph token balance for the active account.

        :return: Integer.
        """
        return await self.get_balance_for(self.address)

    async def get_balance_for(self, address: str) -> int:
        """
        Get Metagraph token balance for the active account.

        :return: Integer.
        """
        response = await self.network.get_address_balance(address)
        if response and isinstance(response.balance, (int, float)):
            return int(response.balance)
        return 0

    async def get_fee_recommendation(self):
        # TODO: Fee api
        last_ref = await self.network.get_address_last_accepted_transaction_ref(
            self.address
        )
        if not last_ref.get("hash"):
            return 0

        last_tx = await self.network.get_pending_transaction(last_ref["hash"])
        if not last_tx:
            return 0

        return 1 / self.token_decimals

    async def create_allow_spend(
        self,
        destination: str,
        amount: int,
        approvers: List[str],
        source: Optional[str] = None,
        fee: int = 0,
        currency_id: Optional[str] = None,
        valid_until_epoch: Optional[int] = None,
    ):
        """
        Grants permission for another wallet or metagraph to spend up to a specified amount from the user’s wallet in a metagraph token or DAG.

        :param source: Wallet address signing the transaction. Address of logged in account, if left None
        :param destination: The destination address. This must be a Metagraph address.
        :param amount: The amount the destination address is allowed to spend.
        :param approvers: A list with single DAG address that can automatically approve the spend, can be Metagraph or wallet address.
        :param currency_id: The Metagraph ID used to identify the currency. For DAG, this parameter is left None.
        :param fee: Default 0.
        :param valid_until_epoch: The global snapshot epoch progress for which this is valid until. If not provided, the default value will be currentEpoch + 30. Minumum allowed value: currentEpoch + 5. Maximum allowed value: currentEpoch + 60.
        """
        # TODO: check logged in and valid private key

        response = await allow_spend(
            destination=destination,
            amount=amount,
            approvers=approvers,
            source=source or self.account.key_trio.address,
            fee=fee,
            currency_id=currency_id or self.network.connected_network.metagraph_id,
            valid_until_epoch=valid_until_epoch,
            network=self.network,
            key_trio=self.account.key_trio,
        )
        return response

    async def create_token_lock(
        self,
        amount: int,
        fee: int = 0,
        unlock_epoch: int = None,
        source: str = None,
        currency_id: Optional[str] = None,
    ):
        """
        Token locking is used for:

        Node collateral staking
        Delegated staking participation
        Governance requirements
        Time-based vesting or escrow models

        :param source: The wallet signing the transaction. The logged in account is the default if left empty.
        :param amount: The amount to lock.
        :param currency_id: The Metagraph identifier address for the currency to lock. Leave None, if currency is DAG.
        :param fee: The fee. Default when None is 0.
        :param unlock_epoch: The global snapshot epoch progress to unlock the tokens. If provided, must be greater than the current epoch.
        """
        # TODO: check logged in and valid private key
        # this.account.assertAccountIsActive();
        # this.account.assertValidPrivateKey();
        #
        response = await token_lock(
            source=source,
            amount=amount,
            fee=fee,
            currency_id=currency_id or self.network.connected_network.metagraph_id,
            unlock_epoch=unlock_epoch,
            network=self.network,
            key_trio=self.account.key_trio,
        )
        return response

    async def transfer(
        self,
        to_address: str,
        amount: int,
        fee: int = 0,
        auto_estimate_fee: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Transfer DAG from active account to another DAG address. Amount as integer with the number of decimals used by the Metagraph.

        :param to_address: DAG address.
        :param amount: Integer with the number of decimals used by the Metagraph.
        :param fee: Integer with the number of decimals used by the Metagraph.
        :param auto_estimate_fee:
        :return: Dictionary.
        """
        # TODO: Fee api endpoint
        last_ref = await self.network.get_address_last_accepted_transaction_ref(
            self.address
        )

        tx, hash_ = await self.account.generate_signed_transaction(
            to_address, amount, fee, last_ref
        )

        tx_hash = await self.network.post_transaction(tx)
        if tx_hash:
            return {
                "timestamp": datetime.now(),
                "hash": tx_hash,
                "amount": amount,
                "receiver": to_address,
                "fee": fee,
                "sender": self.address,
                "ordinal": last_ref.ordinal,
                "pending": True,
                "status": "POSTED",
            }

    async def wait_for_balance_change(self, initial_value: Optional[int] = None):
        """
        Check if active account balance changes (around 2 minutes).

        :param initial_value:
        :return: False if check did not detect balance change, else True.
        """
        if initial_value is None:
            initial_value = await self.get_balance()
            await self.wait(5)

        for _ in range(24):
            result = await self.get_balance()
            if result is not None and result != initial_value:
                return True
            await self.wait(5)

        return False

    async def generate_batch_transactions(
        self,
        transfers: List[Dict[str, Any]],
        last_ref: Optional[Union[Dict[str, Any], TransactionReference]] = None,
    ):
        """
        Takes a list of dictionaries and returns a list of signed transaction objects.

        :param transfers: List of dictionaries.
        :param last_ref: Lost hash and ordinal from DAG address.
        :return:
        """
        if isinstance(last_ref, TransactionReference):
            last_ref = last_ref.model_dump()
        if not last_ref:
            last_ref = await self.network.get_address_last_accepted_transaction_ref(
                self.address
            )
            last_ref = last_ref.model_dump()

        txns = []
        for transfer in transfers:
            transaction, hash_ = await self.account.generate_signed_transaction(
                transfer["to_address"],
                transfer["amount"],
                transfer.get("fee", 0),
                last_ref,
            )
            last_ref = {"hash": hash_, "ordinal": last_ref["ordinal"] + 1}
            txns.append(transaction)

        return txns

    async def transfer_batch_transactions(
        self, transactions: List[SignedTransaction]
    ) -> List[Optional[str]]:
        """
        Send a list of signed transaction objects from the active account.

        :param transactions: List of signed transactions.
        :return: List of transactions.
        """
        hashes = []
        for txn in transactions:
            tx_hash = await self.network.post_transaction(txn)
            hashes.append(tx_hash)
        return hashes

    async def transfer_batch(
        self,
        transfers: List[Dict[str, Any]],
        last_ref: Optional[Union[Dict[str, Any], TransactionReference]] = None,
    ):
        """
        Build and send a list of transactions from the active account.

        :param transfers: List of dictionaries.
        :param last_ref: Last ordinal and hash from active account.
        :return: List of transaction hashes.
        """
        # Metagraph like PACA doesn't seem to support this, needs to wait for the transaction to appear
        txns = await self.generate_batch_transactions(transfers, last_ref)
        return await self.transfer_batch_transactions(txns)

    async def wait(self, time_in_seconds: int = 5):
        """Wait for a number of seconds.

        :param time_in_seconds: Integer.
        """
        await asyncio.sleep(time_in_seconds)
