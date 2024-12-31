from hashlib import sha256
import base58

from coincurve import PrivateKey
from mnemonic import Mnemonic

from .constants import DERIVATION_PATH, COIN, PKCS_PREFIX

# The derivation_path_map together with the seed can be used to derive the extended private key from the public_key
# E.g. "m/44'/{COIN.DAG}'/0'/0" (account 0, index 0); "m/44'/{COIN.DAG}'/0'/1" (account 0, index 1)
DERIVATION_PATH_MAP = {
    DERIVATION_PATH.DAG: f"m/44'/{COIN.DAG}'/0'/0",
    DERIVATION_PATH.ETH: f"m/44'/{COIN.ETH}'/0'/0",
    DERIVATION_PATH.ETH_LEDGER: "m/44'/60'",
}

class Wallet:
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