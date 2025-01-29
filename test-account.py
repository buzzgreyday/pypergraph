import unittest
from unittest import IsolatedAsyncioTestCase

import pypergraph.dag_account
from pypergraph.dag_keyring import KeyringManager

WORDS="solution rookie cake shine hand attack claw awful harsh level case vocal"

class Test(IsolatedAsyncioTestCase):
    async def test_login_connect_send(self):
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

        keyring_controller = KeyringManager()
        await keyring_controller.login('password')
        keyring_wallet = keyring_controller.get_wallet_by_id("MCW1")
        print([k.__dict__ for k in keyring_wallet.keyrings])
        print(keyring_wallet.keyrings[0].accounts[0].key_trio)




if __name__ == '__main__':
    unittest.main()
