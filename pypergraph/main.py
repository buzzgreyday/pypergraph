import asyncio
from os import getenv

from pypergraph.dag_keyring import KeyringManager
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
    await keyring_manager.login('password')
    account = keyring_manager.get_accounts()[0]
    wallet = keyring_manager.get_wallet_for_account(account.address)
    print(wallet.__dict__)
    tx, hash_ = await account.generate_signed_transaction(amount=1,
                                                          to_address="DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN")
    print(tx)
    # Second method
    keyring_manager.set_password('password')
    encrypted_vault = await store.get('vault')
    decrypted_vault = await keyring_manager.encryptor.decrypt(keyring_manager.password, encrypted_vault)
    account = DagAccount()
    account.login_with_seed_phrase(decrypted_vault["wallets"][0]["secret"])
    # last_ref = await network.get_address_last_accepted_transaction_ref(account.address)
    # tx, hash_ = keystore.prepare_tx(amount=1, to_address="DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN", from_address=account.address, last_ref=last_ref)
    # signature = keystore.sign(account.private_key, hash_)
    # proof = {"id": account.public_key[2:], "signature": signature}
    # tx.add_proof(proof)
    tx, hash_ = await account.generate_signed_transaction(amount=1,
                                                          to_address="DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN")
    print(tx)


if __name__ == "__main__":

    # TODO: Keyring modules needs refactoring, storage needs to be implemented and we also need to think about how to proceed from here.
    asyncio.run(main())
