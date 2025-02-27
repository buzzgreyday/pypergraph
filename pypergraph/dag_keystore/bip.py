from bip32utils import BIP32Key
from ecdsa import SigningKey, SECP256k1
from mnemonic import Mnemonic

from .constants import DERIVATION_PATH, DERIVATION_PATH_MAP



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
    def get_public_key_from_private_hex(private_key_hex: str) -> str:
        """
        Derive the public key from a private key using secp256k1.

        :param private_key_hex: The private key in hexadecimal format.
        :return: The public key as a hexadecimal string.
        """
        private_key_bytes = bytes.fromhex(private_key_hex)
        private_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        public_key =  b'\x04' + private_key.get_verifying_key().to_string()
        return public_key.hex()

class Bip39:
    """Generate 12 or 24 words and derive entropy"""
    LANGUAGES = ("english", "chinese_simplified", "chinese_traditional", "french", "italian",
                            "japanese", "korean", "spanish", "turkish", "czech", "portuguese")
    def __init__(self, words: int = 12, language: str = "english"):
        self.strength = 128 if words == 12 else 256 if words == 24 else None
        if self.strength is None:
            raise ValueError(f"Bip39 :: The value or Bip39(words={words} is unsupported. Supported: 12 or 24")
        if language not in Bip39.LANGUAGES:
            raise ValueError(f"Bip39 :: The language {language} isn't supported. Supported languages: {', '.join(Bip39.LANGUAGES)}")
        else:
            self.language = language

    def mnemonic(self) -> dict:
        """
        :return: Dictionary with Mnemonic object, mnemonic phrase, mnemonic seed, mnemonic entropy.
        """
        mnemo = Mnemonic(self.language)
        words = mnemo.generate(strength=self.strength)
        seed = mnemo.to_seed(words, passphrase="")
        entropy = mnemo.to_entropy(words)
        return {"mnemo": mnemo, "words": words, "seed": seed, "entropy": entropy}

    def get_seed_from_mnemonic(self, words: str):
        mnemo = Mnemonic(self.language)
        return mnemo.to_seed(words)

    @staticmethod
    def validate_mnemonic(mnemonic_phrase: str, language: str = "english"):
        mnemo = Mnemonic(language)
        if mnemo.check(mnemonic_phrase):
            return True
        else:
            return False