import pytest
import random

import pypergraph.dag_account
from pypergraph.dag_network.models.network import NetworkInfo
from pypergraph.dag_network.network import DagTokenNetwork


""" NETWORK CONFIGURATION """

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
async def test_get_address_balance(network):
    address = "DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw"
    result = await network.get_address_balance(address)
    assert result.balance >= 0

@pytest.mark.asyncio
async def test_get_total_supply(network):
    result = await network.l0_api.get_total_supply()
    assert bool(result.total_supply)

@pytest.mark.asyncio
async def test_get_cluster_info(network):
    result = await network.l0_api.get_cluster_info()
    assert bool(result)

@pytest.mark.asyncio
async def test_get_latest_l0_snapshot(network):
    result = await network.l0_api.get_latest_snapshot()
    print(result.value)

@pytest.mark.asyncio
async def test_get_latest_snapshot_ordinal(network):
    result = await network.l0_api.get_latest_snapshot_ordinal()
    print(result)


""" L1 API """

@pytest.mark.asyncio
async def test_get_l1_cluster_info(network):
    result = await network.cl1_api.get_cluster_info()
    assert bool(result)

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
async def test_post_transaction(network):
   from .secrets import mnemo, to_address
   account = pypergraph.dag_account.DagAccount()
   account.connect(network_id="testnet")
   if account.network.connected_network.network_id == "testnet":
       account.login_with_seed_phrase(mnemo)
       tx, hash_ = await account.generate_signed_transaction(to_address=to_address, amount=100000000, fee=200000000)

       await account.network.post_transaction(tx)

# @pytest.mark.asyncio
# async def test_post_metagraph_transaction(network):
#     from .secrets import mnemo, to_address, from_address
#     from pypergraph.dag_keystore import KeyStore
#     from pypergraph.dag_core.models.transaction import Proof, Transaction
#     account = pypergraph.dag_account.DagAccount()
#     account.login_with_seed_phrase(mnemo)
#     account_metagraph_client = pypergraph.dag_account.MetagraphTokenClient(account=account, metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43", l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100", cl1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200")
# #     # Generate signed tx
#     last_ref = await account_metagraph_client.network.get_address_last_accepted_transaction_ref(address=from_address)
# #     tx, hash_ = KeyStore.prepare_tx(amount=100000000, to_address=to_address, from_address=from_address, last_ref=last_ref, fee=0)
# #     signature = KeyStore.sign(account_metagraph_client.account.private_key, hash_)
# #     valid = KeyStore.verify(account_metagraph_client.account.public_key, hash_, signature)
# #     if not valid:
# #         raise ValueError("Wallet :: Invalid signature.")
# #     proof = Proof(id=account_metagraph_client.account.public_key[2:], signature=signature)
# #     tx = Transaction(value=tx, proofs=[proof])
#     tx, hash_ = await account_metagraph_client.account.generate_signed_transaction(to_address=to_address, amount=100000000, fee=0, last_ref=last_ref)
#     await account_metagraph_client.network.post_transaction(tx=tx.model_dump())
