import unittest
from unittest import IsolatedAsyncioTestCase

import pypergraph.dag_wallet

WORDS="solution rookie cake shine hand attack claw awful harsh level case vocal"

class Test(IsolatedAsyncioTestCase):
    async def test_login_connect_send(self):
        network_info = {
            "network_id": "testnet",
            "be_url": "https://be-testnet.constellationnetwork.io",
            "l0_host": None,
            "cl1_host": None,
            "l0_lb_url": "https://l0-lb-testnet.constellationnetwork.io",
            "l1_lb_url": "https://l1-lb-testnet.constellationnetwork.io"
        }

        wallet = pypergraph.dag_wallet.DagAccount()
        wallet.login_with_seed_phrase(WORDS)
        wallet.connect(network_info)
        valid = wallet.on("network_change")
        self.assertTrue(valid)
        data = await wallet.send("DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN", 1)
        self.assertEqual("POSTED", data.get("status"))  # add assertion here


if __name__ == '__main__':
    unittest.main()
