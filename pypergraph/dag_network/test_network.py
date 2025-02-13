from random import randint

from pypergraph.dag_core.models.network import NetworkInfo
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
        l0_api_cluster_data = [[d.ip, d.public_port] for d in await self.network.l0_api.get_cluster_info()]
        l0_api_cluster_node = l0_api_cluster_data[randint(0, len(l0_api_cluster_data)-1)]
        l1_api_cluster_data = [[d.ip, d.public_port] for d in await self.network.cl1_api.get_cluster_info()]
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
        el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"

        """HOST/LB"""
        async def test_get_address_balance(self):
            result = await self.network.get_address_balance(self.address)
            self.assertGreaterEqual(result.balance, 0)

        async def test_get_last_ref(self):
            result = await self.network.get_address_last_accepted_transaction_ref(self.address)
            self.assertTrue(bool(result.hash))

        async def test_get_pending(self):
            # Will be None/False if the tx is not pending
            result = await self.network.get_pending_transaction(hash="fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429")
            if result:
                print(result)
            else:
                print("No pending transactions.")

        async def test_get_total_supply(self):
            result = await self.network.l0_api.get_total_supply()
            self.assertGreater(result.total_supply, 100000000)

        async def test_get_cluster_info(self):
            result = await self.network.l0_api.get_cluster_info()
            # Check if result is a list
            self.assertTrue(bool(result))

        """BE"""
        async def test_get_latest_snapshot(self):
            result = await self.network.get_latest_snapshot()
            print(result.hash, result.timestamp, result.ordinal)

        async def test_get_snapshot_by_id(self):
            result = await self.network.be_api.get_snapshot("dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e")
            print(result.hash, result.timestamp, result.ordinal)

        async def test_get_transactions_by_snapshot(self):
            results = await self.network.be_api.get_transactions_by_snapshot("2404170")
            print(results[0].source, results[0].destination, results[0].amount)

        async def test_get_rewards_by_snapshot(self):
            results = await self.network.be_api.get_rewards_by_snapshot(2404170)
            print(results[0].destination, results[0].amount)

        async def test_get_latest_snapshot_transactions(self):
            results = await self.network.be_api.get_latest_snapshot_transactions()
            print(results)

        async def test_get_latest_snapshot_rewards(self):
            results = await self.network.be_api.get_latest_snapshot_rewards()
            print(results)

        async def test_get_transactions(self):
            results = await self.network.be_api.get_transactions(limit=10, search_after=None, search_before=None)
            print(results[0].source, results[0].destination, results[0].amount, results[0].timestamp, results[0].hash)

        async def test_get_transaction(self):
            result = await self.network.be_api.get_transaction("dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e")
            print(result.source, result.destination, result.amount, result.timestamp, result.hash)

        async def test_get_latest_currency_snapshot(self):
            result = await self.network.be_api.get_latest_currency_snapshot(self.el_paca_metagraph_id)
            print(result) # Ordinal: 950075

        async def test_get_currency_snapshot(self):
            result = await self.network.be_api.get_currency_snapshot(self.el_paca_metagraph_id, 950075)
            print(result)

        async def test_get_latest_currency_snapshot_rewards(self):
            results = await self.network.be_api.get_latest_currency_snapshot_rewards(self.el_paca_metagraph_id)
            print(results)

        async def test_get_currency_snapshot_rewards(self):
            results = await self.network.be_api.get_currency_snapshot_rewards(self.el_paca_metagraph_id, 950075)
            print(results)

        async def test_get_currency_block(self):
            results = await self.network.be_api.get_currency_block(self.el_paca_metagraph_id, "b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364")
            print(results)

        async def test_get_currency_address_balance(self):
            result = await self.network.be_api.get_currency_address_balance(self.el_paca_metagraph_id, "b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364")
            print(result)



if __name__ == '__main__':
    unittest.main()
