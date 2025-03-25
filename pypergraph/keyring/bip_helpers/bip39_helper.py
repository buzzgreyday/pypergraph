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