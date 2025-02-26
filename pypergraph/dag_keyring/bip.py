from bip32utils import BIP32Key
from mnemonic import Mnemonic


class Bip39Helper:
    """Generate 12 or 24 words and derive entropy"""
    LANGUAGES = ("english", "chinese_simplified", "chinese_traditional", "french", "italian",
                            "japanese", "korean", "spanish", "turkish", "czech", "portuguese")
    def __init__(self, words: int = 12, language: str = "english"):
        self.strength = 128 if words == 12 else 256 if words == 24 else None
        if self.strength is None:
            raise ValueError(f"Bip39 :: The value or Bip39(words={words} is unsupported. Supported: 12 or 24")
        if language not in Bip39Helper.LANGUAGES:
            raise ValueError(f"Bip39 :: The language {language} isn't supported. Supported languages: {', '.join(self.LANGUAGES)}")
        else:
            self.language = language

    def generate_mnemonic(self) -> str:
        """
        :return: Dictionary with Mnemonic object, mnemonic phrase, mnemonic seed, mnemonic entropy.
        """
        mnemo = Mnemonic(self.language)
        return mnemo.generate(strength=self.strength)

    def is_valid(self, seed: str) -> bool:
        """
        Validates the mnemonic phrase and returns bool.

        :param self:
        :param seed: Mnemonic phrase.
        :return:
        """

        mnemo = Mnemonic(self.language)
        return mnemo.check(seed)

    def get_seed_bytes_from_mnemonic(self, mnemonic: str):
        mnemo = Mnemonic(self.language)
        return mnemo.to_seed(mnemonic)

class Bip32Helper:
    @staticmethod
    def get_root_key_from_seed(seed_bytes) -> BIP32Key:
        """
        Derive the HD root/master key from a seed entropy in bytes format.

        :param seed_bytes: The seed entropy in bytes format.
        :return: The root/master key.
        """
        return BIP32Key.fromEntropy(seed_bytes)


    def get_hd_root_key_from_seed(self, seed_bytes: bytes, hd_path: str) -> BIP32Key:
        """
        Derive the private key from a seed entropy using derived path.

        :param seed_bytes: The seed in bytes format.
        :param hd_path: The derivation path.
        :return: The private key as a hexadecimal string.
        """
        path_parts = [int(part.strip("'")) for part in hd_path.split("/")[1:]]
        purpose = path_parts[0] + 2 ** 31
        coin_type = path_parts[1] + 2 ** 31
        account = path_parts[2] + 2 ** 31
        change = 0
        index = path_parts[3]
        root_key = self.get_root_key_from_seed(seed_bytes=seed_bytes)
        return root_key.ChildKey(purpose).ChildKey(coin_type).ChildKey(account).ChildKey(change).ChildKey(
            index)
