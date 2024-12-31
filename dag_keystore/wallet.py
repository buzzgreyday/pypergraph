from hashlib import sha256
import base58

from bip32utils import BIP32Key
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

class Bip39:
    """Generate 12 or 24 words and derive entropy"""
    LANGUAGES = ("english", "chinese_simplified", "chinese_traditional", "french", "italian",
                            "japanese", "korean", "spanish", "turkish", "czech", "portuguese")
    def __init__(self, words: int = 12, language: str = "english"):
        self.strength = 128 if words == 12 else 256 if words == 24 else None
        if self.strength is None:
            raise ValueError(f"The value or Bip39(words={words} is unsupported. Supported: 12 or 24")
        if language not in Bip39.LANGUAGES:
            ValueError(f"The language {language} isn't supported. Supported languages: {', '.join(Bip39.LANGUAGES)}")
        else:
            self.language = language

    def mnemonic(self):

        mnemo = Mnemonic(self.language)
        words = mnemo.generate(strength=self.strength)
        seed = mnemo.to_seed(words, passphrase="")
        entropy = mnemo.to_entropy(words)
        return {"mnemo": mnemo, "words": words, "seed": seed, "entropy": entropy}

    def get_seed_from_mnemonic(self, words: str):
        mnemo = Mnemonic(self.language)
        return mnemo.to_seed(words)

class Bip32:
    @staticmethod
    def get_root_key_from_seed(seed_bytes):
        """
        Derive the HD root/master key from a seed entropy in bytes format.

        :param seed_bytes: The seed entropy in bytes format.
        :return: The root/master key.
        """
        return BIP32Key.fromEntropy(seed_bytes)

    @staticmethod
    def get_private_key_from_seed(seed_bytes, derivation_path: str = DERIVATION_PATH.DAG):
        """
        Derive the private key from a seed entropy using derived path.

        :param seed_bytes: The seed in bytes format.
        :param derivation_path: The derivation path.
        :return: The private key as a hexadecimal string.
        """
        path = DERIVATION_PATH_MAP[derivation_path]
        path_parts = [int(part.strip("'")) for part in path.split("/")[1:]]
        purpose = path_parts[0] + 2**31
        coin_type = path_parts[1] + 2**31
        account = path_parts[2] + 2**31
        change = 0
        index = path_parts[3]
        root_key = Bip32().get_root_key_from_seed(seed_bytes=seed_bytes)
        return root_key.ChildKey(purpose).ChildKey(coin_type).ChildKey(account).ChildKey(change).ChildKey(index).PrivateKey()

    @staticmethod
    def get_public_key_from_private_hex(private_key_hex: str, compressed: bool = False):
        """
        Derive the public key from a private key using secp256k1.

        :param private_key_hex: The private key in hexadecimal format.
        :param compressed: Whether to return a compressed public key.
        :return: The public key as a hexadecimal string.
        """
        private_key_bytes = bytes.fromhex(private_key_hex)
        private_key = PrivateKey(private_key_bytes)
        public_key = private_key.public_key.format(compressed=compressed)
        return public_key


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
