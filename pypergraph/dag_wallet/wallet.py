import asyncio
from typing import Optional, Self

from pypergraph.dag_keystore import KeyStore, Bip39, TransactionV2
from pypergraph.dag_network import Network


class Wallet:

    def __init__(self, address: str, public_key: str, private_key: str, words: Optional[str] = None,  network=None):
        self.address = address
        self.public_key = public_key
        self.private_key = private_key
        self.words = words
        self.network = network or Network()  # Automatically set a default API instance

    def __repr__(self):
        return f"Wallet(address={self.address}, public_key={self.public_key}, private_key={self.private_key}, words={self.words}, network={self.network!r})"


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
        private_key = KeyStore.get_private_key_from_seed(seed_bytes)
        public_key = KeyStore.get_public_key_from_private_key(private_key)
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
        :param l0_host: IP and PORT or URL associated with the network or metagraph (required if metagraph_id is set).
        :param l1_host: IP and PORT or URL associated with the network or metagraph (required if metagraph_id is set).
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

    def get_pending_transaction(self, transaction_hash: str):
        """
        Asynchronous method (used with await)

        :param transaction_hash:
        :return: Async task: pending transaction
        """
        return asyncio.create_task(self.network.get_pending_transaction(transaction_hash=transaction_hash))
