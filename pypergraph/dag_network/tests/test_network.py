import pytest
import random
from pypergraph.dag_core.models.network import NetworkInfo
from pypergraph.dag_network.network import DagTokenNetwork

@pytest.fixture
def network():
    return DagTokenNetwork()

@pytest.mark.parametrize("network_id, expected", [
    ("testnet", NetworkInfo(
        network_id='testnet',
        be_url='https://be-testnet.constellationnetwork.io',
        l0_host='https://l0-lb-testnet.constellationnetwork.io',
        cl1_host='https://l1-lb-testnet.constellationnetwork.io',
        l0_lb_url='https://l0-lb-testnet.constellationnetwork.io',
        l1_lb_url='https://l1-lb-testnet.constellationnetwork.io')
    ),
    ("integrationnet", NetworkInfo(
        network_id='integrationnet',
        be_url='https://be-integrationnet.constellationnetwork.io',
        l0_host='https://l0-lb-integrationnet.constellationnetwork.io',
        cl1_host='https://l1-lb-integrationnet.constellationnetwork.io',
        l0_lb_url='https://l0-lb-integrationnet.constellationnetwork.io',
        l1_lb_url='https://l1-lb-integrationnet.constellationnetwork.io')
    ),
    ("mainnet", NetworkInfo(
        network_id='mainnet',
        be_url='https://be-mainnet.constellationnetwork.io',
        l0_host='https://l0-lb-mainnet.constellationnetwork.io',
        cl1_host='https://l1-lb-mainnet.constellationnetwork.io',
        l0_lb_url='https://l0-lb-mainnet.constellationnetwork.io',
        l1_lb_url='https://l1-lb-mainnet.constellationnetwork.io')
    ),
    (None, NetworkInfo(
        network_id='mainnet',
        be_url='https://be-mainnet.constellationnetwork.io',
        l0_host='https://l0-lb-mainnet.constellationnetwork.io',
        cl1_host='https://l1-lb-mainnet.constellationnetwork.io',
        l0_lb_url='https://l0-lb-mainnet.constellationnetwork.io',
        l1_lb_url='https://l1-lb-mainnet.constellationnetwork.io')
    )
])
def test_init_network(network_id, expected):
    net = DagTokenNetwork(network_id) if network_id else DagTokenNetwork()
    assert net.get_network() == expected.__dict__

@pytest.mark.asyncio
async def test_init_custom(network):
    l0_api_cluster_data = [[d.ip, d.public_port] for d in await network.l0_api.get_cluster_info()]
    if not l0_api_cluster_data:
        pytest.skip("No L0 cluster nodes available")
    l0_api_cluster_node = random.choice(l0_api_cluster_data)
    l1_api_cluster_data = [[d.ip, d.public_port] for d in await network.cl1_api.get_cluster_info()]
    if not l1_api_cluster_data:
        pytest.skip("No L1 cluster nodes available")
    l1_api_cluster_node = random.choice(l1_api_cluster_data)

    net = DagTokenNetwork(
        network_id="mainnet",
        l0_host=f"http://{l0_api_cluster_node[0]}:{l0_api_cluster_node[1]}",
        cl1_host=f"http://{l1_api_cluster_node[0]}:{l1_api_cluster_node[1]}"
    )

    expected = NetworkInfo(
        network_id="mainnet",
        be_url='https://be-mainnet.constellationnetwork.io',
        l0_host=f"http://{l0_api_cluster_node[0]}:{l0_api_cluster_node[1]}",
        cl1_host=f"http://{l1_api_cluster_node[0]}:{l1_api_cluster_node[1]}",
        l0_lb_url='https://l0-lb-mainnet.constellationnetwork.io',
        l1_lb_url='https://l1-lb-mainnet.constellationnetwork.io'
    )
    assert net.get_network() == vars(expected)

def test_config_network(network):
    assert network.connected_network.network_id == "mainnet"
    network.config("integrationnet")
    expected = NetworkInfo(
        network_id='integrationnet',
        be_url='https://be-integrationnet.constellationnetwork.io',
        l0_host='https://l0-lb-integrationnet.constellationnetwork.io',
        cl1_host='https://l1-lb-integrationnet.constellationnetwork.io',
        l0_lb_url='https://l0-lb-integrationnet.constellationnetwork.io',
        l1_lb_url='https://l1-lb-integrationnet.constellationnetwork.io'
    )
    assert network.get_network() == expected.__dict__

@pytest.mark.asyncio
async def test_get_address_balance(network):
    address = "DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw"
    result = await network.get_address_balance(address)
    assert result.balance >= 0

@pytest.mark.asyncio
async def test_get_last_ref(network):
    address = "DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw"
    result = await network.get_address_last_accepted_transaction_ref(address)
    assert bool(result.hash)

@pytest.mark.asyncio
async def test_get_pending(network):
    result = await network.get_pending_transaction(
        hash="fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429"
    )
    if result:
        print(result)
    else:
        print("No pending transactions.")

@pytest.mark.asyncio
async def test_get_total_supply(network):
    result = await network.l0_api.get_total_supply()
    assert result.total_supply > 100000000

@pytest.mark.asyncio
async def test_get_cluster_info(network):
    result = await network.l0_api.get_cluster_info()
    assert bool(result)

""" Block Explorer """
@pytest.mark.asyncio
async def test_get_latest_snapshot(network):
    result = await network.get_latest_snapshot()
    assert result.hash and result.timestamp and result.ordinal, "Snapshot data should not be empty"

@pytest.mark.asyncio
async def test_get_snapshot_by_id(network):
    result = await network.be_api.get_snapshot(
        "2404170"
    )
    assert result.hash and result.timestamp and result.ordinal, "Snapshot data should not be empty"

@pytest.mark.asyncio
async def test_get_transactions_by_snapshot(network):
    results = await network.be_api.get_transactions_by_snapshot("2404170")
    assert results[0].source and results[0].destination and results[0].amount, "Transaction data should not be empty"

@pytest.mark.asyncio
async def test_get_rewards_by_snapshot(network):
    results = await network.be_api.get_rewards_by_snapshot(2404170)
    print(results[0].destination, results[0].amount)

@pytest.mark.asyncio
async def test_get_latest_snapshot_transactions(network):
    results = await network.be_api.get_latest_snapshot_transactions()
    print(results)

@pytest.mark.asyncio
async def test_get_latest_snapshot_rewards(network):
    results = await network.be_api.get_latest_snapshot_rewards()
    print(results)

@pytest.mark.asyncio
async def test_get_transactions(network):
    results = await network.be_api.get_transactions(limit=10)
    print(results[0].source, results[0].destination, results[0].amount, results[0].timestamp, results[0].hash)

@pytest.mark.asyncio
async def test_get_transaction(network):
    result = await network.be_api.get_transaction(
        "dc30b8063bcb5def3206e0134244ba4f12f5c283aabc3d4d74c35bfd9ce7e03e"
    )
    print(result.source, result.destination, result.amount, result.timestamp, result.hash)

@pytest.mark.asyncio
async def test_get_latest_currency_snapshot(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    result = await network.be_api.get_latest_currency_snapshot(el_paca_metagraph_id)
    print(result)

@pytest.mark.asyncio
async def test_get_currency_snapshot(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    result = await network.be_api.get_currency_snapshot(el_paca_metagraph_id, 950075)
    print(result)

@pytest.mark.asyncio
async def test_get_latest_currency_snapshot_rewards(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    results = await network.be_api.get_latest_currency_snapshot_rewards(el_paca_metagraph_id)
    print(results)

@pytest.mark.asyncio
async def test_get_currency_snapshot_rewards(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    results = await network.be_api.get_currency_snapshot_rewards(el_paca_metagraph_id, 950075)
    print(results)

#@pytest.mark.asyncio
#async def test_get_currency_block(network):
#    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
#    results = await network.be_api.get_currency_block(
#        el_paca_metagraph_id,
#        "b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364",
#    )
#    print(results)

@pytest.mark.asyncio
async def test_get_currency_address_balance(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    result = await network.be_api.get_currency_address_balance(
        el_paca_metagraph_id,
        "b54515a603499925d011a86d784749c523905ca492c82d9bf938414918349364",
    )
    print(result)

@pytest.mark.asyncio
async def test_get_currency_transaction(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    result = await network.be_api.get_currency_transaction(
        el_paca_metagraph_id,
        "121b672f1bc4819985f15a416de028cf57efe410d63eec3e6317a5bc53b4c2c7",
    )
    print(result)

@pytest.mark.asyncio
async def test_get_currency_transactions(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    results = await network.be_api.get_currency_transactions(metagraph_id=el_paca_metagraph_id, limit=10)
    print(results[0].source, results[0].destination, results[0].amount, results[0].timestamp, results[0].hash)

@pytest.mark.asyncio
async def test_get_currency_transactions_by_address(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    results = await network.be_api.get_currency_transactions_by_address(metagraph_id=el_paca_metagraph_id, address="DAG6qWERv6BdrEztpc7ufXmpgJAjDKdF2RKZAqXY", limit=10)
    print(results[0].source, results[0].destination, results[0].amount, results[0].timestamp, results[0].hash)

@pytest.mark.asyncio
async def test_get_currency_transactions_by_snapshot(network):
    el_paca_metagraph_id = "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43"
    results = await network.be_api.get_currency_transactions_by_snapshot(metagraph_id=el_paca_metagraph_id, hash_or_ordinal=952394, limit=10)
    print(results[0].source, results[0].destination, results[0].amount, results[0].timestamp, results[0].hash)


""" L0 API """
@pytest.mark.asyncio
async def test_get_latest_snapshot(network):
    result = await network.l0_api.get_latest_snapshot()
    print(result.value)