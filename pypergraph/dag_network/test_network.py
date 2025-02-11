from random import randint

from .models import NetworkInfo
from .network import DagTokenNetwork
import unittest


class TestInitNetworkConfig(unittest.IsolatedAsyncioTestCase):
    network = DagTokenNetwork()
    def test_init_testnet(self):
        network = DagTokenNetwork("testnet")
        valid_network = NetworkInfo(
                             network_id='testnet',
                             be_url='https://be-testnet.constellationnetwork.io',
                             l0_host='https://l0-lb-testnet.constellationnetwork.io',
                             cl1_host='https://l1-lb-testnet.constellationnetwork.io',
                             l0_lb_url='https://l0-lb-testnet.constellationnetwork.io',
                             l1_lb_url='https://l1-lb-testnet.constellationnetwork.io'
        )
        self.assertEqual(network.get_network(), valid_network.__dict__)

    def test_init_intnet(self):
        network = DagTokenNetwork("integrationnet")
        valid_network = NetworkInfo(
                             network_id='integrationnet',
                             be_url='https://be-integrationnet.constellationnetwork.io',
                             l0_host='https://l0-lb-integrationnet.constellationnetwork.io',
                             cl1_host='https://l1-lb-integrationnet.constellationnetwork.io',
                             l0_lb_url='https://l0-lb-integrationnet.constellationnetwork.io',
                             l1_lb_url='https://l1-lb-integrationnet.constellationnetwork.io'
        )
        self.assertEqual(network.get_network(), valid_network.__dict__)

    def test_init_mainnet(self):
        network = DagTokenNetwork("mainnet")
        valid_network = NetworkInfo(
            network_id='mainnet',
            be_url='https://be-mainnet.constellationnetwork.io',
            l0_host='https://l0-lb-mainnet.constellationnetwork.io',
            cl1_host='https://l1-lb-mainnet.constellationnetwork.io',
            l0_lb_url='https://l0-lb-mainnet.constellationnetwork.io',
            l1_lb_url='https://l1-lb-mainnet.constellationnetwork.io'
        )
        self.assertEqual(network.get_network(), valid_network.__dict__)

    def test_init_default(self):
        network = DagTokenNetwork()
        valid_network = NetworkInfo(
            network_id='mainnet',
            be_url='https://be-mainnet.constellationnetwork.io',
            l0_host='https://l0-lb-mainnet.constellationnetwork.io',
            cl1_host='https://l1-lb-mainnet.constellationnetwork.io',
            l0_lb_url='https://l0-lb-mainnet.constellationnetwork.io',
            l1_lb_url='https://l1-lb-mainnet.constellationnetwork.io'
        )
        self.assertEqual(network.get_network(), valid_network.__dict__)

    async def test_init_custom(self):
        l0_api_cluster_data = [[d["ip"], d["publicPort"]] for d in await self.network.l0_api.get_cluster_info()]
        l0_api_cluster_node = l0_api_cluster_data[randint(0, len(l0_api_cluster_data)-1)]
        l1_api_cluster_data = [[d["ip"], d["publicPort"]] for d in await self.network.cl1_api.get_cluster_info()]
        l1_api_cluster_node = l1_api_cluster_data[randint(0, len(l1_api_cluster_data)-1)]
        network = DagTokenNetwork(network_id="mainnet", l0_host=f"http://{l0_api_cluster_node[0]}:{l0_api_cluster_node[1]}", cl1_host=f"http://{l1_api_cluster_node[0]}:{l1_api_cluster_node[1]}")
        valid_network = NetworkInfo(
            network_id="mainnet",
            be_url='https://be-mainnet.constellationnetwork.io',
            l0_host=f"http://{l0_api_cluster_node[0]}:{l0_api_cluster_node[1]}",
            cl1_host=f"http://{l1_api_cluster_node[0]}:{l1_api_cluster_node[1]}",
            l0_lb_url='https://l0-lb-mainnet.constellationnetwork.io',
            l1_lb_url='https://l1-lb-mainnet.constellationnetwork.io'
        )
        self.assertEqual(network.get_network(), valid_network.__dict__)

    def test_config_network(self):
        self.assertEqual(self.network.connected_network.network_id, "mainnet")
        self.network.config("integrationnet")
        valid_network = NetworkInfo(
                             network_id='integrationnet',
                             be_url='https://be-integrationnet.constellationnetwork.io',
                             l0_host='https://l0-lb-integrationnet.constellationnetwork.io',
                             cl1_host='https://l1-lb-integrationnet.constellationnetwork.io',
                             l0_lb_url='https://l0-lb-integrationnet.constellationnetwork.io',
                             l1_lb_url='https://l1-lb-integrationnet.constellationnetwork.io'
        )
        self.assertEqual(self.network.get_network(), valid_network.__dict__)

    class TestGetData(unittest.IsolatedAsyncioTestCase):

        address = "DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw"
        network = DagTokenNetwork()

        async def test_get_address_balance(self):
            balance = await self.network.get_address_balance(self.address)

        async def test_get_last_ref(self):
            last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)

        async def test_get_pending(self):
            pending_tx = await self.network.get_pending_transaction(hash="fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429")

        async def test_get_total_supply(self):
            total_supply = await self.network.l0_api.get_total_supply()

        async def test_get_cluster_info(self):
            cluster_info = await self.network.l0_api.get_cluster_info()
            print(cluster_info)



if __name__ == '__main__':
    unittest.main()
