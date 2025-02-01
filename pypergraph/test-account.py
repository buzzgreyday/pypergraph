import json
import unittest
from unittest import IsolatedAsyncioTestCase

from docutils.nodes import address

import pypergraph.dag_account
from pypergraph.dag_account import DagAccount
from pypergraph.dag_keyring import KeyringManager
from pypergraph.dag_keystore import KeyStore
from pypergraph.dag_network import DagTokenNetwork
from pypergraph.dag_keyring.storage import StateStorageDb

WORDS="solution rookie cake shine hand attack claw awful harsh level case vocal"

class Test(IsolatedAsyncioTestCase):
    async def test_simple_account(self):
        network_info = {
            "network": "Constellation",
            "network_id": "testnet",
            "be_url": "https://be-testnet.constellationnetwork.io",
            "l0_host": None,
            "cl1_host": None,
            "l0_lb_url": "https://l0-lb-testnet.constellationnetwork.io",
            "l1_lb_url": "https://l1-lb-testnet.constellationnetwork.io"
        }

        wallet = pypergraph.dag_account.DagAccount()
        wallet.login_with_seed_phrase(WORDS)
        print(wallet.address)
        wallet.connect(network_info)
        valid = wallet.emitter.on("network_change")
        self.assertTrue(valid)
        keyring_manager = KeyringManager()
        keyring_manager.set_password('password')
        await keyring_manager.create_or_restore_vault("My Wallet", WORDS, keyring_manager.password)
        #data = await wallet.send("DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN", 1)
        #self.assertEqual("POSTED", data.get("status"))  # add assertion here

    async def test_keyring_account(self):
        keyring_manager = KeyringManager()
        keystore = KeyStore()
        network = DagTokenNetwork()
        store = StateStorageDb()
        await keyring_manager.login('password')
        await keyring_manager.create_or_restore_vault("My Wallet", WORDS, keyring_manager.password)
        account = keyring_manager.get_accounts()[0]
        wallet = keyring_manager.get_wallet_for_account(account.get_address())
        account.login_with_seed_phrase(wallet.mnemonic)
        print(wallet.__dict__)
        tx, hash_ = await account.generate_signed_transaction(amount=1, to_address="DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN")
        print(tx)
        # Second method
        keyring_manager.set_password('password')
        encrypted_vault = await store.get('vault')
        decrypted_vault = await keyring_manager.encryptor.decrypt(keyring_manager.password, encrypted_vault)
        account = DagAccount()
        account.login_with_seed_phrase(decrypted_vault["wallets"][0]["secret"])
        #last_ref = await network.get_address_last_accepted_transaction_ref(account.address)
        #tx, hash_ = keystore.prepare_tx(amount=1, to_address="DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN", from_address=account.address, last_ref=last_ref)
        #signature = keystore.sign(account.private_key, hash_)
        #proof = {"id": account.public_key[2:], "signature": signature}
        #tx.add_proof(proof)
        tx, hash_ = await account.generate_signed_transaction(amount=1, to_address="DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN")
        print(tx)




if __name__ == '__main__':
    unittest.main()
