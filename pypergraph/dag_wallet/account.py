import asyncio
from typing import Self

from pypergraph.dag_keystore import KeyStore, KeyTrio, Bip39, TransactionV2, Bip32
from pypergraph.dag_network import Network
from pypergraph.dag_network.network import DagTokenNetwork

from decimal import Decimal
from pyee.asyncio import AsyncIOEventEmitter
from typing import Optional, List

DAG_DECIMALS = Decimal('100000000')  # Assuming DAG uses 8 decimals


class DagAccount(AsyncIOEventEmitter):
    def __init__(self, network = None):
        super().__init__()
        self.network = network or DagTokenNetwork()
        self.key_trio = None

    def connect(self, network_info: dict):
        print("Connecting to:", network_info)
        self.network.config(network_info)

        return self

    @property
    def address(self):
        if not self.key_trio or not self.key_trio.get("address"):
            raise ValueError("DagAccount :: Need to login before calling methods on DagAccount.")
        return self.key_trio["address"]

    @property
    def public_key(self):
        return self.key_trio.get("public_key")

    @property
    def private_key(self):
        return self.key_trio.get("private_key")

    def login_with_seed_phrase(self, words: str):
        seed_bytes = Bip39().get_seed_from_mnemonic(words)
        private_key = KeyStore.get_private_key_from_mnemonic(seed_bytes)
        print(words, private_key)
        self.login_with_private_key(private_key)

    def login_with_private_key(self, private_key: str):
        public_key = Bip32.get_public_key_from_private_hex(private_key)
        #public_key = KeyStore.get_public_key_from_private(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key)
        self._set_keys_and_address(private_key, public_key, address)

    def login_with_public_key(self, public_key: str):
        address = KeyStore.get_dag_address_from_public_key(public_key)
        self._set_keys_and_address(None, public_key, address)

    def is_active(self):
        return self.key_trio is not None

    def logout(self):
        self.key_trio = None
        self.emit("session_change", True)

    def observe_session_change(self, listener):
        self.on("session_change", listener)

    def _set_keys_and_address(self, private_key: Optional[str], public_key: str, address: str):
        self.key_trio = {
            "private_key": private_key,
            "public_key": public_key,
            "address": address
        }
        self.emit("session_change", True)

    async def get_balance(self):
        return await self.get_balance_for(self.address)

    async def get_balance_for(self, address: str):
        address_obj = await self.network.get_address_balance(address)
        if address_obj and "balance" in address_obj:
            return Decimal(address_obj["balance"]) * DAG_DECIMALS
        return Decimal(0)

    async def generate_signed_transaction(self, to_address: str, amount: Decimal, fee: Decimal = 0, last_ref=None):
        last_ref = last_ref or await self.network.get_address_last_accepted_transaction_ref(self.address)
        tx, hash_ = KeyStore.prepare_tx(amount, to_address, self.key_trio["address"], last_ref, fee)
        signature = KeyStore.sign(self.key_trio["private_key"], hash_)
        valid = KeyStore.verify(self.public_key, hash_, signature)
        if not valid:
            raise ValueError("Wallet :: Invalid signature.")
        proof = {"id": self.public_key[2:], "signature": signature}
        tx.add_proof(proof=proof)
        return tx.serialize(), hash_


    async def send(self, to_address: str, amount: Decimal, fee: Decimal = 0, auto_estimate_fee=False):
        # TODO: Rate limiting
        normalized_amount = int(amount * DAG_DECIMALS)
        print("Getting last transaction:")
        last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)

        if fee == Decimal(0) and auto_estimate_fee:
            pending_tx = await self.network.get_pending_transaction(last_ref.get("prev_hash", last_ref.get("hash")))

            if pending_tx:
                balance_obj = await self.network.get_address_balance(self.address)

                if balance_obj and Decimal(balance_obj["balance"]) == normalized_amount:
                    amount -= Decimal(1) / DAG_DECIMALS
                    normalized_amount -= 1

                fee = Decimal(1) / DAG_DECIMALS

        signed_tx, hash_ = await self.generate_signed_transaction(to_address, amount, fee)
        tx_hash = await self.network.post_transaction(signed_tx)

        if tx_hash:
            # TODO: Tax software standards
            return {
                #"timestamp": self.network.get_current_time(),
                "hash": tx_hash,
                "amount": amount,
                "receiver": to_address,
                "fee": fee,
                "sender": self.address,
                "ordinal": last_ref.get("ordinal"),
                "pending": True,
                "status": "POSTED",
            }

    async def wait_for_checkpoint_accepted(self, hash: str):
        txn = None
        try:
            txn = await self.network.get_pending_transaction(hash)
        except Exception:
            pass

        if txn and txn.get("status") == "Waiting":
            return True

        try:
            await self.network.get_transaction(hash)
        except Exception:
            return False

        return True


    async def wait_for_balance_change(self, initial_value: Optional[Decimal] = None):
        if initial_value is None:
            initial_value = await self.get_balance()
            await self.wait(5)

        for _ in range(24):
            result = await self.get_balance()

            if result is not None and result != initial_value:
                return True

            await self.wait(5)

        return False

    async def generate_batch_transactions(self, transfers: List[dict], last_ref: Optional[dict] = None):

        if not last_ref:
            last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)

        txns = []
        for transfer in transfers:
            transaction, hash_ = await self.generate_signed_transaction(
                transfer["address"],
                transfer["amount"],
                transfer["fee"],
                last_ref
            )

            last_ref = {
                "hash": hash_,
                "ordinal": last_ref["ordinal"] + 1,
            }

            txns.append(transaction)

        return txns

    async def send_batch_transactions(self, transactions: List[dict]):
        if self.network.get_network_version() == "1.0":
            raise Exception("transferDagBatch not available for mainnet 1.0")

        hashes = []
        for txn in transactions:
            hash_ = await self.network.post_transaction(txn)
            hashes.append(hash_)

        return hashes

    async def transfer_dag_batch(self, transfers: List[dict], last_ref: Optional[dict] = None):
        txns = await self.generate_batch_transactions(transfers, last_ref)
        return await self.send_batch_transactions(txns)

    # def create_metagraph_token_client(self, network_info: dict):
    #     return MetagraphTokenClient(self, network_info)

    async def wait(self, time: float = 5.0):
        from asyncio import sleep
        await sleep(time)


class OldDagAccount:

    def __init__(self, address: str, public_key: str, private_key: str, words: Optional[str] = None,  network=None):
        self.address = address
        self.public_key = public_key
        self.private_key = private_key
        self.words = words
        self.network = DagTokenNetwork()  # Automatically set a default API instance

    def __repr__(self):
        return f"Account(address={self.address}, public_key={self.public_key}, private_key={self.private_key}, words={self.words}, network={self.network!r})"


    @classmethod
    def new(cls):
        """
        Create a new wallet.

        :return: Configured wallet object.
        """
        mnemonic_values = KeyStore.get_mnemonic()
        private_key = KeyStore.get_private_key_from_seed(seed=mnemonic_values["seed"])
        public_key = KeyStore.get_public_key_from_private_key(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key_hex=public_key)
        valid = KeyStore.validate_dag_address(address=address)
        if not valid:
            raise ValueError("Wallet :: Not a valid DAG address.")
        return cls(
            address=address,
            public_key=public_key,
            private_key=private_key,
            words=mnemonic_values["words"]
        )

    @classmethod
    def from_mnemonic(cls, words: str):
        """
        Create a wallet from an existing mnemonic phrase.

        :param words: String of 12 words separated by spaces.
        :return: Configured wallet object.
        """
        valid = KeyStore.validate_mnemonic(mnemonic_phrase=words)
        if not valid:
            raise ValueError("Wallet :: Not a valid mnemonic.")
        mnemonic = Bip39()
        seed_bytes = mnemonic.get_seed_from_mnemonic(words)
        private_key = KeyStore.get_private_key_from_mnemonic(seed_bytes)
        public_key = KeyStore.get_public_key_from_private(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key)
        valid = KeyStore.validate_dag_address(address=address)
        if not valid:
            raise ValueError("Wallet :: Not a valid DAG address.")
        return cls(
            address=address,
            public_key=public_key,
            private_key=private_key,
            words=words
        )

    @classmethod
    def from_private_key(cls, private_key: str):
        """
        Create a wallet from an existing private key.

        :param private_key: Private key as a hexadecimal string.
        :return: Configured wallet object.
        """
        public_key = KeyStore.get_public_key_from_private_key(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key)
        valid = KeyStore.validate_dag_address(address=address)
        if not valid:
            raise ValueError("Wallet :: Not a valid DAG address.")
        return cls(
            address=address,
            public_key=public_key,
            private_key=private_key
        )

    async def transaction(self, to_address: str, amount: float, fee: float = 0.0) -> TransactionV2:
        """
        :param to_address: The address to receive transaction
        :param amount: Quantity to send to the address
        :param fee: Tip the network
        :return: TransactionV2 object
        """
        last_ref = await self.network.get_last_reference(address_hash=self.address)
        tx, tx_hash, encoded_tx = KeyStore.prepare_tx(amount=amount, to_address=to_address, from_address=self.address,
                                                      last_ref=last_ref.to_dict(), fee=fee)
        signature = KeyStore.sign(private_key_hex=self.private_key, tx_hash=tx_hash)
        valid = KeyStore.verify(public_key_hex=self.public_key, tx_hash=tx_hash, signature_hex=signature)
        if not valid:
            raise ValueError("Wallet :: Invalid signature.")
        proof = {"id": self.public_key[2:], "signature": signature}
        tx.add_proof(proof=proof)
        return tx

    def send(self, tx: TransactionV2):
        """
        Asynchronous method (used with await).
        Sends the transaction using the current wallet configuration.

        :param tx: Transaction object.
        :return: Response from the configured network.
        """
        return asyncio.create_task(self.network.post_transaction(tx.get_post_transaction()))

    def set_network(self, network: str = "mainnet", l0_host: str | None = None, l1_host: str | None = None, metagraph_id: str | None = None) -> Self:
        """
        Choose the network and layer associated with the wallet.

        :param network: The network API to use with the wallet: "testnet", "integrationnet", "mainnet" (default: "mainnet").
        :param metagraph_id: DAG address associated with the metagraph (required if metagraph_id is set).
        :param l0_host: IP and PORT or URL associated with the network or metagraph (required if metagraph_id is set), including "http://" or "https://" prefix.
        :param l1_host: IP and PORT or URL associated with the network or metagraph (required if metagraph_id is set), including "http://" or "https://" prefix.
        :return: Configured wallet object.
        """
        self.network = Network(network=network, l0_host=l0_host, l1_host=l1_host, metagraph_id=metagraph_id)
        return self

    def get_address_balance(self, dag_address: str | None = None, metagraph_id: str | None = None):
        """
        Asynchronous method (used with await).

        :param metagraph_id: This identifier is the DAG address associated with the metagraph.
        :param dag_address:
        :return: Async task: DAG wallet balance in float.
        """
        dag_address = self.address if not dag_address else dag_address
        metagraph_id = self.network.metagraph_id if not metagraph_id else metagraph_id
        return asyncio.create_task(self.network.get_address_balance(dag_address=dag_address, metagraph_id=metagraph_id))

    def key_trio(self):
        """
        This object can be transformed to a dictionary with the '.to_dict()' method.
        :return: KeyTrio object with 'private_key', 'public_key' and 'address'.
        """
        return KeyTrio(private_key=self.private_key, public_key=self.public_key, address=self.address)

    def get_pending_transaction(self, transaction_hash: str):
        """
        Asynchronous method (used with await)

        :param transaction_hash:
        :return: Async task: pending transaction
        """
        return asyncio.create_task(self.network.get_pending_transaction(transaction_hash=transaction_hash))
