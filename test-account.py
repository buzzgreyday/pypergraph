import unittest
from unittest import IsolatedAsyncioTestCase

from docutils.nodes import address

import pypergraph.dag_account
from pypergraph.dag_keyring import KeyringManager
from pypergraph.dag_keystore import KeyStore
from pypergraph.dag_network import DagTokenNetwork

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
        #data = await wallet.send("DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN", 1)
        #self.assertEqual("POSTED", data.get("status"))  # add assertion here

    async def test_keyring_account(self):
        manager = KeyringManager()
        keystore = KeyStore()
        network = DagTokenNetwork()
        await manager.login('password')
        wallet = manager.get_wallet_by_id('MCW1')
        # We need some way of easily generating signed transactions.
        # There's one keyring per chain; each containing DagAccounts and EthAccounts, respectively
        print([k.__dict__ for k in wallet.keyrings])
        print([a for k in wallet.keyrings for a in k.__dict__])
        pub_key = wallet.keyrings[0].accounts[0].get_public_key()
        address = wallet.keyrings[0].accounts[0].get_address()
        priv_key = wallet.keyrings[0].accounts[0].get_private_key()
        last_ref = await network.get_address_last_accepted_transaction_ref(address)
        tx, hash_ = keystore.prepare_tx(amount=1, to_address="DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN", from_address=address, last_ref=last_ref)
        signature = keystore.sign(priv_key, hash_)
        proof = {"id": pub_key[2:], "signature": signature}
        tx.add_proof(proof)
        print(tx.serialize())




if __name__ == '__main__':
    unittest.main()
