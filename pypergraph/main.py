import asyncio
from os import getenv

from pypergraph.dag_core import BIP_44_PATHS, KeyringNetwork
from pypergraph.dag_keyring import KeyringManager
from pypergraph.dag_keystore import Bip32
from mnemonic import Mnemonic

WORDS = getenv("WORDS")

if __name__ == "__main__":

    # TODO: Keyring modules needs refactoring, storage needs to be implemented and we also need to think about how to proceed from here.

    manager = KeyringManager()
    hd_wallet = asyncio.run(manager.create_or_restore_vault(label='', seed=WORDS, password='password'))

    seed_bytes = Mnemonic("english").to_seed(WORDS)

    # This is going to be used often
    path = BIP_44_PATHS.CONSTELLATION_PATH.value
    path_parts = [int(part.strip("'")) for part in path.split("/")[1:]]
    purpose = path_parts[0] + 2 ** 31
    coin_type = path_parts[1] + 2 ** 31
    account = path_parts[2] + 2 ** 31
    change = 0
    index = path_parts[3]
    root_key = Bip32().get_root_key_from_seed(seed_bytes=seed_bytes)
    root_key = root_key.ChildKey(purpose).ChildKey(coin_type).ChildKey(account).ChildKey(change).ChildKey(index)

    s_wallet = asyncio.run(manager.create_single_account_wallet(label="", network=KeyringNetwork.Constellation.value, private_key=root_key.PrivateKey()))
    print(hd_wallet.export_secret_key())
    print(s_wallet.export_secret_key())