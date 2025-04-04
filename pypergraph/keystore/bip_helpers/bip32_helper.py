from typing import Dict

from bip32utils import BIP32Key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from pypergraph.core import BIP_44_PATHS
from .bip39_helper import Bip39Helper

def parse_path(path) -> Dict:
    path_parts = [int(part.strip("'")) for part in path.split("/")[1:]]
    purpose = path_parts[0] + 2**31
    coin_type = path_parts[1] + 2**31
    account = path_parts[2] + 2**31
    change = path_parts[3]
    return {'purpose': purpose, 'coin_type': coin_type, 'account': account, 'change': change}

class Bip32Helper:
    @staticmethod
    def get_root_key_from_seed(seed: bytes):
        """
        Derive the HD root/master key from a seed entropy in bytes format.

        :param seed: The seed entropy in bytes format.
        :return: The root/master key.
        """
        return BIP32Key.fromEntropy(seed)

    def get_master_key_from_mnemonic(self, phrase: str, path = BIP_44_PATHS.CONSTELLATION_PATH.value):
        bip39 = Bip39Helper()
        path = parse_path(path)
        seed = bip39.get_seed_from_mnemonic(phrase)
        root_key = self.get_root_key_from_seed(seed=seed)
        return root_key.ChildKey(path['purpose']).ChildKey(path['coin_type']).ChildKey(path['account']).ChildKey(path['change'])

    def get_private_key_from_seed(self, seed: bytes, path = BIP_44_PATHS.CONSTELLATION_PATH.value):
        """
        Derive the private key from a seed entropy using derived path.

        :param seed: The seed in bytes format.
        :param path: The derivation path.
        :return: The private key as a hexadecimal string.
        """
        INDEX = 0
        path = parse_path(path)
        root_key = self.get_root_key_from_seed(seed=seed)
        return root_key.ChildKey(path['purpose']).ChildKey(path['coin_type']).ChildKey(path['account']).ChildKey(path['change']).ChildKey(INDEX).PrivateKey()

    @staticmethod
    def get_public_key_from_private_hex(private_key: bytes) -> str:
        """
        Derive the public key from a private key using secp256k1.

        :param private_key: The private key in hexadecimal format.
        :return: The uncompressed public key as a hexadecimal string with 04 prefix.
        """
        # Convert hex private key to cryptography object
        private_key_int = int.from_bytes(private_key, byteorder='big')
        private_key = ec.derive_private_key(
            private_key_int, ec.SECP256K1(), default_backend()
        )
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        return public_bytes.hex() # has 04 prefix
