from mnemonic import Mnemonic

class Bip39Helper:
    """Generate 12 or 24 words and derive entropy"""
    LANGUAGES = ("english", "chinese_simplified", "chinese_traditional", "french", "italian",
                            "japanese", "korean", "spanish", "turkish", "czech", "portuguese")
    def __init__(self, words: int = 12, language: str = "english"):
        self.strength = 128 if words == 12 else 256 if words == 24 else None
        if self.strength is None:
            raise ValueError(f"Bip39 :: The value or Bip39(words={words} is unsupported. Supported: 12 or 24")
        if language not in self.LANGUAGES:
            raise ValueError(f"Bip39 :: The language {language} isn't supported. Supported languages: {', '.join(self.LANGUAGES)}")
        else:
            self.language = language

    def mnemonic(self) -> str:
        """
        :return: Dictionary with Mnemonic object, mnemonic phrase, mnemonic seed, mnemonic entropy.
        """
        mnemo = Mnemonic(self.language)
        phrase = mnemo.generate(strength=self.strength)
        #seed = mnemo.to_seed(words)
        #entropy = mnemo.to_entropy(words)
        return phrase

    def get_seed_from_mnemonic(self, phrase: str):
        mnemo = Mnemonic(self.language)
        return mnemo.to_seed(phrase)

    @staticmethod
    def validate_mnemonic(mnemonic_phrase: str, language: str = "english"):
        mnemo = Mnemonic(language)
        if mnemo.check(mnemonic_phrase):
            return True
        else:
            return False