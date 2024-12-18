from coincurve import PrivateKey
from mnemonic import Mnemonic
from bip32utils import BIP32Key
from hashlib import sha256
import base58

class DERIVATION_PATH:
    DAG = "DAG"
    ETH = "ETH"
    ETH_LEDGER = "ETH_LEDGER"


class COIN:
    DAG = 1137
    ETH = 60


DERIVATION_PATH_MAP = {
    DERIVATION_PATH.DAG: f"m/44'/{COIN.DAG}'/0'/0",
    DERIVATION_PATH.ETH: f"m/44'/{COIN.ETH}'/0'/0",
    DERIVATION_PATH.ETH_LEDGER: "m/44'/60'",
}

PKCS_PREFIX = "3056301006072a8648ce3d020106052b8104000a034200"  # Removed last 2 digits. 04 is part of Public Key.


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
    def get_private_key_from_seed(seed_bytes, derivation_path: str = DERIVATION_PATH.DAG) -> str:
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
        return root_key.ChildKey(purpose).ChildKey(coin_type).ChildKey(account).ChildKey(change).ChildKey(index).PrivateKey().hex()

    @staticmethod
    def get_public_key_from_private_hex(private_key_hex: str, compressed: bool = False) -> str:
        """
        Derive the public key from a private key using secp256k1.

        :param private_key_hex: The private key in hexadecimal format.
        :param compressed: Whether to return a compressed public key.
        :return: The public key as a hexadecimal string.
        """
        private_key_bytes = bytes.fromhex(private_key_hex)
        private_key = PrivateKey(private_key_bytes)
        public_key = private_key.public_key.format(compressed=compressed)
        return public_key.hex()


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

        wallet_address = f"DAG{check_digit}{public_key}"
        return wallet_address

def main():
    bip39 = Bip39()
    bip32 = Bip32()
    wallet = Wallet()
    mnemonic_values = bip39.mnemonic()
    private_key = bip32.get_private_key_from_seed(seed_bytes=mnemonic_values["seed"])
    public_key = bip32.get_public_key_from_private_hex(private_key_hex=private_key)
    dag_addr = wallet.get_dag_address_from_public_key_hex(public_key_hex=public_key)
    print("Values:", mnemonic_values, "\nPrivate Key: " + private_key, "\nPublic Key: " + public_key, "\nDAG Address: " + dag_addr)

if __name__ == "__main__":
    main()



