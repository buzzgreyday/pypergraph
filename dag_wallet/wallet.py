import asyncio
from hashlib import sha256
from typing import Optional

import base58

from mnemonic import Mnemonic

from dag_keystore import KeyStore, Bip39
from dag_network import API
from .constants import DERIVATION_PATH, COIN, PKCS_PREFIX

# The derivation_path_map together with the seed can be used to derive the extended private key from the public_key
# E.g. "m/44'/{COIN.DAG}'/0'/0" (account 0, index 0); "m/44'/{COIN.DAG}'/0'/1" (account 0, index 1)
DERIVATION_PATH_MAP = {
    DERIVATION_PATH.DAG: f"m/44'/{COIN.DAG}'/0'/0",
    DERIVATION_PATH.ETH: f"m/44'/{COIN.ETH}'/0'/0",
    DERIVATION_PATH.ETH_LEDGER: "m/44'/60'",
}

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
        Derive the DAG address from the public key.

        :param public_key_hex: The private key in hexadecimal format.
        :return: The DAG address corresponding with the public key.
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
    def get_mnemonic_from_input():
        """
        Prompts the user to enter a mnemonic word seed, validates it, and returns it.
        """
        mnemo = Mnemonic("english")
        while True:
            user_input = input("Enter your mnemonic seed phrase: ").strip()

            # Split the input into words and check length
            words = user_input.split()
            if len(words) not in (12, 15, 18, 21, 24):
                print("Invalid seed length. It should have 12, 15, 18, 21, or 24 words. Please try again.")
                continue

            # Validate mnemonic
            if mnemo.check(user_input):
                print("Mnemonic is valid.")
                return user_input
            else:
                print("Invalid mnemonic. Please ensure it is correct.")

    @classmethod
    def new(cls):
        mnemonic_values = KeyStore.get_mnemonic()
        private_key = KeyStore.get_private_key_from_seed(seed=mnemonic_values["seed"])
        public_key = KeyStore.get_public_key_from_private_key(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key=public_key)
        return cls(
            address=address,
            public_key=public_key,
            private_key=private_key,
            words=mnemonic_values["words"]
        )

    @classmethod
    def from_mnemonic(cls, words: str):
        """
        :param words: String of 12 words
        :return: Wallet object
        """
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
        public_key = KeyStore.get_public_key_from_private_key(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key)
        return cls(
            address=address,
            public_key=public_key,
            private_key=private_key
        )

    async def build_transaction(self, to_address: str, amount: float, fee: float = 0.0):
        from_address = self.address
        last_ref = await self.api.get_last_reference(dag_address=self.address)
        tx, tx_hash, encoded_tx = KeyStore.prepare_tx(amount, to_address, from_address, last_ref, fee)
        signature = KeyStore.sign(private_key_hex=self.private_key, tx_hash=tx_hash)
        proof = {"id": self.public_key[2:], "signature": signature}
        tx.add_proof(proof=proof)
        return tx

    def send(self, tx):
        return asyncio.create_task(self.api.post_transaction(tx.get_post_transaction()))

    def set_api(self, network=None, layer=None):
        """Update the API parameters."""
        if network not in (None, "mainnet", "testnat", "integrationnet"):
            raise ValueError(f"Network must be None or 'mainnet' or 'integrationnet' or 'testnet'")
        if layer not in (None, 0, 1):
            raise ValueError(f"Network must be None or integer 0 or 1")
        network = network or self.api.network
        layer = layer if layer is not None else self.api.layer
        self.api = API(network=network, layer=layer)
        return self

