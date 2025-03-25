from typing import Dict

from bip32utils import BIP32Key
from ecdsa import SigningKey, SECP256k1

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

        :param seed_bytes: The seed entropy in bytes format.
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

        :param private_key_bytes: The private key in hexadecimal format.
        :return: The public key as a hexadecimal string.
        """
        private_key = SigningKey.from_string(private_key, curve=SECP256k1)
        public_key =  b'\x04' + private_key.get_verifying_key().to_string()
        return public_key.hex()