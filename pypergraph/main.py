import asyncio
import json
from os import getenv

from cryptography.exceptions import InvalidKey

from pypergraph.dag_keyring import KeyringManager, Encryptor
from pypergraph.dag_account.account import DagAccount
from pypergraph.dag_keyring.storage import StateStorageDb
from pypergraph.dag_keystore import KeyStore
from pypergraph.dag_network import DagTokenNetwork

WORDS = getenv("WORDS")

async def main():
    keyring_manager = KeyringManager()
    keystore = KeyStore()
    network = DagTokenNetwork()
    store = StateStorageDb()
    vault_system = Encryptor(iterations=100000)

    data = {
        "type": "HD Key Tree",
        "data": {
            "mnemonic": "urban december whale coral galaxy",
            "numberOfAccounts": 1,
            "hdPath": "m/44'/60'/0'/0"
        }
    }

    # Create HD Wallet Vault
    hd_vault = await Encryptor().encrypt(
        password="secure_password_123",
        data={
            "type": "HD",
            "mnemonic": "urban december whale coral galaxy ...",
            "numberOfAccounts": 3,
            "hdPath": "m/44'/60'/0'/0"
        }
    )
    print("Encrypted Vault:")
    print(json.dumps(hd_vault, indent=2))
    # Decrypt vault
    try:
        decrypted = await Encryptor().decrypt(
            password="secure_password_123",
            vault=hd_vault
        )
        print("\nDecrypted Data:")
        print(json.dumps(decrypted, indent=2))
    except (InvalidKey, ValueError) as e:
        print(f"Decryption failed: {str(e)}")


    # Create Non-HD Wallet Vault
    non_hd_vault = await Encryptor().encrypt(
        password="another_secure_password",
        data={
            "type": "non-HD",
            "keys": [{
                "privateKey": "0x...",
                "address": "0x..."
            }]
        }
    )

    # Create vault
    print("Encrypted Vault:")
    print(json.dumps(non_hd_vault, indent=2))

    # Decrypt vault
    try:
        decrypted = await vault_system.decrypt("another_secure_password", non_hd_vault)
        print("\nDecrypted Data:")
        print(json.dumps(decrypted, indent=2))
    except (InvalidKey, ValueError) as e:
        print(f"Decryption failed: {str(e)}")



if __name__ == "__main__":

    # TODO: Keyring modules needs refactoring, storage needs to be implemented and we also need to think about how to proceed from here.
    asyncio.run(main())
