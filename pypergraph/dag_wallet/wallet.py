import asyncio
from hashlib import sha256
from typing import Optional

import base58

from pypergraph.dag_keystore import KeyStore, Bip39, TransactionV2
from pypergraph.dag_network import API
from .constants import PKCS_PREFIX


class Wallet:

    def __init__(self, address: str, public_key: str, private_key: str, words: Optional[str] = None,  api=None):
        self.address = address
        self.public_key = public_key
        self.private_key = private_key
        self.words = words
        self.api = api or API()  # Automatically set a default API instance

    def __repr__(self):
        return f"Wallet(address={self.address}, public_key={self.public_key}, private_key={self.private_key}, words={self.words}, api={self.api!r})"

    @staticmethod
    def get_dag_address_from_public_key_hex(public_key_hex: str) -> str:
        """
        :param public_key_hex: The private key as a hexadecimal string.
        :return: The DAG address corresponding to the public key (node ID).
        """
        if len(public_key_hex) == 128:
            public_key = PKCS_PREFIX + "04" + public_key_hex
        elif len(public_key_hex) == 130 and public_key_hex[:2] == "04":
            public_key = PKCS_PREFIX + public_key_hex
        else:
            raise ValueError("Not a valid public key")

        public_key = sha256(bytes.fromhex(public_key)).hexdigest()
        public_key = base58.b58encode(bytes.fromhex(public_key)).decode()
        public_key = public_key[len(public_key) - 36:]

        check_digits = "".join([char for char in public_key if char.isdigit()])
        check_digit = 0
        for n in check_digits:
            check_digit += int(n)
            if check_digit >= 9:
                check_digit = check_digit % 9

        dag_addr = f"DAG{check_digit}{public_key}"
        return dag_addr

    @staticmethod
    def get_mnemonic_from_input() -> str:
        """
        Mostly for testing purposes. Prompts the user to enter a mnemonic seed phrase.

        :return: A mnemonic phrase from user input (should be validated).
        """

        while True:
            user_input = input("Enter your mnemonic seed phrase: ").strip()

            # Split the input into words and check length
            words = user_input.split()
            if len(words) not in (12, 15, 18, 21, 24):
                print("Invalid seed length. It should have 12, 15, 18, 21, or 24 words. Please try again.")
                continue

            return user_input


    @classmethod
    def new(cls):
        """
        Create a new wallet.

        :return: Configured wallet object.
        """
        mnemonic_values = KeyStore.get_mnemonic()
        private_key = KeyStore.get_private_key_from_seed(seed=mnemonic_values["seed"])
        public_key = KeyStore.get_public_key_from_private_key(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key=public_key)
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
        from_address = self.address
        last_ref = await self.api.get_last_reference(address_hash=self.address)
        tx, tx_hash, encoded_tx = KeyStore.prepare_tx(amount, to_address, from_address, last_ref.to_dict(), fee)
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
        return asyncio.create_task(self.api.post_transaction(tx.get_post_transaction()))

    def set_network(self, network=None, layer=None, host=None, metagraph_id=None):
        """
        Choose the network and layer associated with the wallet.

        :param network: The network API to use with the wallet: "testnet", "integrationnet", "mainnet" (default: "mainnet").
        :param layer: The layer to use with the wallet: 0 or 1 (default: 1)
        :param metagraph_id: DAG address associated with the metagraph (required if network="metagraph").
        :param host: IP and port or URL associated with the network or metagraph (required if network="metagraph").
        :return: Configured wallet object.
        """
        if metagraph_id and not host:
            raise ValueError(f"API :: The parameter 'host' can't be empty.")
        network = network or self.api.network
        layer = layer or self.api.layer
        host = host or self.api.host
        metagraph_id = metagraph_id or self.api.metagraph_id
        self.api = API(network=network, layer=layer, host=host, metagraph_id=metagraph_id)
        return self

    def get_address_balance(self, dag_address: str | None = None, metagraph_id: str | None = None):
        """
        Asynchronous method (used with await).

        :param metagraph_id: This identifier is the DAG address associated with the metagraph.
        :param dag_address:
        :return: Async task: DAG wallet balance in float.
        """
        dag_address = self.address if not dag_address else dag_address
        metagraph_id = self.api.metagraph_id if not metagraph_id else metagraph_id
        return asyncio.create_task(self.api.get_address_balance(dag_address=dag_address, metagraph_id=metagraph_id))

    def get_pending_transaction(self, transaction_hash: str):
        """
        Asynchronous method (used with await)

        :param transaction_hash:
        :return: Async task: pending transaction
        """
        return asyncio.create_task(self.api.get_pending_transaction(transaction_hash=transaction_hash))
