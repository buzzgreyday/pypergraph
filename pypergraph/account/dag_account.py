import logging
from datetime import datetime
from typing import Optional, Union, Tuple, List
from typing_extensions import Self

from rx.subject import Subject

from pypergraph.account.models.key_trio import KeyTrio
from pypergraph.keystore import KeyStore
from pypergraph.network import DagTokenNetwork
from pypergraph.network.models.transaction import TransactionStatus, TransactionReference, SignedTransaction, SignatureProof, PendingTransaction


class DagAccount:
    def __init__(self):
        self.network: DagTokenNetwork = DagTokenNetwork()
        self.key_trio: Optional[KeyTrio] = None
        self._session_change: Subject = Subject()

    def connect(
        self,
        network_id: Optional[str] = "mainnet",
        be_url: Optional[str] = None,
        l0_host: Optional[str] = None,
        cl1_host: Optional[str] = None
    ) -> "DagAccount":
        """
        Configure the DagAccount network instance. Parameter 'network_id' can be used to change between 'testnet',
        'integrationnet' or 'mainnet', without further parameter settings. Default: 'mainnet'.

        :param network_id: 'mainnet', 'integrationnet', 'testnet' or any string value.
        :param be_url: Block Explorer host URL.
        :param l0_host: Layer 0 host URL.
        :param cl1_host: Currency Layer 1 host URL.
        :return: Configured DagAccount object.
        """

        # self.network = DagTokenNetwork() This will stop monitor from emitting network changes
        self.network.config(network_id, be_url, l0_host, cl1_host)
        return self

    @property
    def address(self):
        """
        Requires login. Get the DagAccount DAG address.
        See: login_with_seed_phrase(words=), login_with_private_key(private_key=) and login_with_public_key(public_key=)

        :return: DAG address.
        """
        if not self.key_trio or not self.key_trio.address:
            raise ValueError("DagAccount :: Need to login before calling methods on DagAccount.")
        return self.key_trio.address

    @property
    def public_key(self):
        """
        Requires login. Get the DagAccount public key.
        See: login_with_seed_phrase(words=), login_with_private_key(private_key=) and login_with_public_key(public_key=)

        This method does not support transfer of data or currency, due to missing private key.

        :return: Public key.
        """
        if not self.key_trio or not self.key_trio.public_key:
            raise ValueError("DagAccount :: Need to login before calling methods on DagAccount.")
        return self.key_trio.public_key

    @property
    def private_key(self):
        """
        Requires login. Get the DagAccount private key.
        See: login_with_seed_phrase(words=), login_with_private_key(private_key=) and login_with_public_key(public_key=)

        :return: Private key.
        """
        if not self.key_trio or not self.key_trio.private_key:
            raise ValueError("DagAccount :: Need to login before calling methods on DagAccount.")
        return self.key_trio.private_key

    def login_with_seed_phrase(self, phrase: str):
        """
        Login with a 12 word seed phrase. Before transferring data or currency you need to login using a seed phrase
        or private key.

        :param phrase: 12 word seed phrase.
        :return:
        """
        private_key = KeyStore.get_private_key_from_mnemonic(phrase)
        self.login_with_private_key(private_key)

    def login_with_private_key(self, private_key: str):
        """
        Login with a private key. Before transferring data or currency you need to login using a seed phrase
        or private key.

        :param private_key: Private key.
        :return:
        """
        public_key = KeyStore.get_public_key_from_private(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key)
        self._set_keys_and_address(private_key, public_key, address)

    def login_with_public_key(self, public_key: str):
        """
        Login with public key. This method does not enable the account to transfer data or currency.
        See: login_with_seed_phrase(words=) or login_with_private_key(private_key=)

        :param public_key:
        :return:
        """
        address = KeyStore.get_dag_address_from_public_key(public_key)
        self._set_keys_and_address(None, public_key, address)

    def is_active(self):
        """
        Check if any account is logged in.

        :return:
        """
        return self.key_trio is not None

    def logout(self):
        """
        Logout the active account (delete key trio).

        :return:
        """
        self.key_trio = None
        try:
            self._session_change.on_next({"module": "account", "event": "logout"})
        except Exception as e:
            # logger.error(f"Error in network change handler: {e}")
            print(f"Error in DagAccount session change handler: {e}")

    def _set_keys_and_address(self, private_key: Optional[str], public_key: str, address: str):
        self.key_trio = KeyTrio(private_key=private_key, public_key=public_key, address=address)
        try:
            self._session_change.on_next({"module": "account", "event": "login"})
        except Exception as e:
            # logger.error(f"Error in network change handler: {e}")
            print(f"Error in DagAccount session change handler: {e}")

    async def get_balance(self):
        """
        Get the balance for the active account.

        :return:
        """
        return await self.get_balance_for(self.address)

    async def get_balance_for(self, address: str):
        """
        Get balance for a given DAG address. Returned as integer with 8 decimals.

        :param address: DAG address.
        :return: 0 or 8 decimal integer.
        """
        response = await self.network.get_address_balance(address)
        if response:
            return int(response.balance)
        return 0

    async def generate_signed_transaction(
        self,
        to_address: str,
        amount: int,
        fee: int = 0,
        last_ref: Optional[Union[dict, TransactionReference]] = None,
    ) -> Tuple[SignedTransaction, str]:
        """
        Generate a signed currency transaction from the currently active account.

        :param to_address: Recipient DAG address.
        :param amount: Integer with 8 decimals constituting the amount to transfer from the active account.
        :param fee: (Optional) a minimum fee might be required if the active account is transaction limited.
        :param last_ref: (Optional) The ordinal and hash of the last transaction from the active account.
        :return: Signed transaction and the transaction hash.
        """
        if isinstance(last_ref, dict):
            last_ref = TransactionReference(**last_ref)
        last_ref = last_ref or await self.network.get_address_last_accepted_transaction_ref(self.address)
        tx, hash_ = KeyStore.prepare_tx(
            amount=amount,
            to_address=to_address,
            from_address=self.key_trio.address,
            last_ref=last_ref,
            fee=fee,
        )
        signature = KeyStore.sign(self.key_trio.private_key, hash_)
        valid = KeyStore.verify(self.public_key, hash_, signature)
        if not valid:
            raise ValueError("Wallet :: Invalid signature.")
        proof = SignatureProof(id=self.public_key[2:], signature=signature)
        tx = SignedTransaction(value=tx, proofs=[proof])
        return tx, hash_

    async def transfer(
        self, to_address: str, amount: int, fee: int = 0, auto_estimate_fee=False
    ) -> PendingTransaction:
        """
        Build currency transaction, sign and transfer from the active account.

        :param to_address: DAG address
        :param amount: Integer with 8 decimals (e.g. 100000000 = 1 DAG)
        :param fee: Integer with 8 decimals (e.g. 20000 = 0.0002 DAG)
        :param auto_estimate_fee:
        :return:
        """
        # TODO: API fee estimate endpoint
        last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)

        signed_tx, hash_ = await self.generate_signed_transaction(to_address, amount, fee)
        tx_hash = await self.network.post_transaction(signed_tx)

        if tx_hash:
            pending_tx = PendingTransaction(
                timestamp=int(datetime.now().timestamp() * 1000),
                hash=tx_hash,
                amount=amount,
                receiver=to_address,
                fee=fee,
                sender=self.address,
                ordinal=last_ref.ordinal,
                pending=True,
                status=TransactionStatus.POSTED,
            )
            return pending_tx

    async def wait_for_checkpoint_accepted(self, hash: str):
        """
        Check if transaction has been processed.

        :param hash: Transaction hash.
        :return: True if processed, False if not processed.
        """
        txn = None
        try:
            txn = await self.network.get_pending_transaction(hash)
        except Exception:
            logging.debug("DagAccount :: No pending transaction.")

        if txn and txn.get("status") == "Waiting":
            return True

        try:
            await self.network.get_transaction(hash)
        except Exception:
            return False

        return True

    async def wait_for_balance_change(self, initial_value: Optional[int] = None):
        """
        Check if balance changed since initial value.

        :param initial_value:
        :return: True if balance changed, False if no change.
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
        transfers: List[dict],
        last_ref: Optional[Union[dict, TransactionReference]] = None,
    ):
        """
        Generate a batch of transactions to be transferred from the active account.

        :param transfers: List of dictionaries, e.g. txn_data = [
            {'to_address': to_address, 'amount': 10000000, 'fee': 200000},
            {'to_address': to_address, 'amount': 5000000, 'fee': 200000},
            {'to_address': to_address, 'amount': 2500000, 'fee': 200000},
            {'to_address': to_address, 'amount': 1, 'fee': 200000}
            ]
        :param last_ref: (Optional) Dictionary or with the account's last transaction hash and ordinal.
        :return: List of transactions to be transferred (see: transfer_batch_transactions(transactions=))
        """
        if isinstance(last_ref, dict):
            last_ref = TransactionReference(**last_ref)
        if not last_ref:
            last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)

        txns = []
        for transfer in transfers:
            transaction, hash_ = await self.generate_signed_transaction(
                to_address=transfer["to_address"],
                amount=transfer["amount"],
                fee=transfer.get("fee", 0),
                last_ref=last_ref,
            )
            last_ref = TransactionReference(ordinal=last_ref.ordinal + 1, hash=hash_)
            txns.append(transaction)

        return txns

    async def transfer_batch_transactions(self, transactions: List[SignedTransaction]):
        """
        Send a batch (list) of signed currency transactions.

        :param transactions: [SignedTransaction, ... ]
        :return: List of transaction hashes.
        """
        hashes = []
        for txn in transactions:
            hash_ = await self.network.post_transaction(txn)
            hashes.append(hash_)
        return hashes

    async def transfer_batch(
        self,
        transfers: List[dict],
        last_ref: Optional[Union[dict, TransactionReference]] = None,
    ):
        """
        Build and send $DAG currency transactions.

        :param transfers: List of dictionaries, e.g. txn_data = [
            {'to_address': to_address, 'amount': 10000000, 'fee': 200000},
            {'to_address': to_address, 'amount': 5000000, 'fee': 200000},
            {'to_address': to_address, 'amount': 2500000, 'fee': 200000},
            {'to_address': to_address, 'amount': 1, 'fee': 200000}
            ]
        :param last_ref: Dictionary with former ordinal and transaction hash, e.g.: {'ordinal': x, 'hash': y}.
        :return:
        """
        txns = await self.generate_batch_transactions(transfers, last_ref)
        return await self.transfer_batch_transactions(txns)

    def get_eth_address(self) -> str:
        # TODO
        raise NotImplementedError("DagAccount :: Method not implemented.")

    def create_metagraph_token_client(
        self,
        account: Optional[Self] = None,
        metagraph_id: Optional[str] = None,
        block_explorer_url: Optional[str] = None,
        l0_host: Optional[str] = None,
        currency_l1_host: Optional[str] = None,
        data_l1_host: Optional[str] = None,
        token_decimals: int = 8,
    ):
        """
        Derive a Metagraph client from the active account to interact with a Metagraph.

        :param account: active DagAccount.
        :param metagraph_id: Associated Metagraph $DAG address.
        :param block_explorer_url: (Optional) Block Explorer URL (default: associated account).
        :param l0_host: (Optional) Layer 0 host URL (port might be required).
        :param cl1_host: (Optional) Layer 1 currency host URL (port might be required).
        :param dl1_host: (Optional) Layer 1 data host URL (port might be required).
        :param token_decimals: (Optional) 1 $DAG = 100000000 (default: 8)
        :return: Metagraph token client object.
        """
        from pypergraph.account import MetagraphTokenClient

        return MetagraphTokenClient(
            account=account or self,
            metagraph_id=metagraph_id or self.network.connected_network.metagraph_id,
            block_explorer_url=block_explorer_url or self.network.connected_network.block_explorer_url,
            l0_host=l0_host,
            currency_l1_host=currency_l1_host,
            data_l1_host=data_l1_host,
            token_decimals=token_decimals,
        )

    async def wait(self, time: float = 5.0):
        from asyncio import sleep

        await sleep(time)