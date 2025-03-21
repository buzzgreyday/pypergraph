import httpx
import pytest

from pypergraph.core.exceptions import NetworkError
from pypergraph.network import DagTokenNetwork
from pypergraph.account import DagAccount, MetagraphTokenClient
from pypergraph.network.models import PendingTransaction


@pytest.fixture
def network():
    return DagTokenNetwork()

@pytest.mark.asyncio
async def test_dag_account_connect(network):
    """Configure the network connection."""
    account = DagAccount()
    account.connect(network_id="testnet")
    assert account.network.get_network() == {
        'dl1_host': None,
        'network_id': 'testnet',
        'be_url': 'https://be-testnet.constellationnetwork.io',
        'l0_lb_url': 'https://l0-lb-testnet.constellationnetwork.io',
        'l1_lb_url': 'https://l1-lb-testnet.constellationnetwork.io',
        'l0_host': 'https://l0-lb-testnet.constellationnetwork.io',
        'cl1_host': 'https://l1-lb-testnet.constellationnetwork.io',
        'metagraph_id': None
    }
    account.connect(network_id="integrationnet")
    assert account.network.get_network() == {
        'dl1_host': None,
        'network_id': 'integrationnet',
        'be_url': 'https://be-integrationnet.constellationnetwork.io',
        'l0_lb_url': 'https://l0-lb-integrationnet.constellationnetwork.io',
        'l1_lb_url': 'https://l1-lb-integrationnet.constellationnetwork.io',
        'l0_host': 'https://l0-lb-integrationnet.constellationnetwork.io',
        'cl1_host': 'https://l1-lb-integrationnet.constellationnetwork.io',
        'metagraph_id': None
    }
    account.connect(network_id="mainnet")
    assert account.network.get_network() == {
        'dl1_host': None,
        'network_id': 'mainnet',
        'be_url': 'https://be-mainnet.constellationnetwork.io',
        'l0_lb_url': 'https://l0-lb-mainnet.constellationnetwork.io',
        'l1_lb_url': 'https://l1-lb-mainnet.constellationnetwork.io',
        'l0_host': 'https://l0-lb-mainnet.constellationnetwork.io',
        'cl1_host': 'https://l1-lb-mainnet.constellationnetwork.io',
        'metagraph_id': None
    }
    account.connect(network_id="mainnet", l0_host='http://123.123.13.123:9000', cl1_host='http://123.123.123.123:9010')
    assert account.network.get_network() == {
        'dl1_host': None,
        'network_id': 'mainnet',
        'be_url': 'https://be-mainnet.constellationnetwork.io',
        'l0_lb_url': 'https://l0-lb-mainnet.constellationnetwork.io',
        'l1_lb_url': 'https://l1-lb-mainnet.constellationnetwork.io',
        'l0_host': 'http://123.123.13.123:9000',
        'cl1_host': 'http://123.123.123.123:9010',
        'metagraph_id': None
    }

@pytest.mark.asyncio
async def test_metagraph_account_connect(network):
    """
    account.network_id is either ethereum or constellation, account.network.network_id is either mainnet,
    integrationnet or testnet. Lb should get reset and be_url should be set as
    get_currency_transactions by address is using BE
    :param network:
    :return:
    """
    from secret import mnemo
    account = DagAccount()
    account.connect(network_id='testnet')
    account.login_with_seed_phrase(mnemo)
    metagraph_account = MetagraphTokenClient(
        account=account,
        l0_host='http://123.123.123.123:9000',
        dl1_host='http://123.123.123.123:9020',
        cl1_host='http://123.123.123.123:9010',
        metagraph_id='DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43'
    )
    metagraph_account.network.get_network()
    assert metagraph_account.network.get_network() == {
        'dl1_host': 'http://123.123.123.123:9020',
        'network_id': 'testnet',
        'be_url': 'https://be-testnet.constellationnetwork.io',
        'l0_lb_url': 'https://l0-lb-testnet.constellationnetwork.io',
        'l1_lb_url': 'https://l1-lb-testnet.constellationnetwork.io',
        'l0_host': 'http://123.123.123.123:9000',
        'cl1_host': 'http://123.123.123.123:9010',
        'metagraph_id': 'DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43'
    }
    metagraph_account = account.create_metagraph_token_client(
        metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        cl1_host='http://123.123.123.123:9010'
    )
    assert metagraph_account.network.get_network() == {
        'dl1_host': None,
        'network_id': 'testnet',
        'be_url': 'https://be-testnet.constellationnetwork.io',
        'l0_lb_url': 'https://l0-lb-testnet.constellationnetwork.io',
        'l1_lb_url': 'https://l1-lb-testnet.constellationnetwork.io',
        'l0_host': 'https://l0-lb-testnet.constellationnetwork.io',
        'cl1_host': 'http://123.123.123.123:9010',
        'metagraph_id': 'DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43'
    }
    try:
        await metagraph_account.get_balance()
    except (ValueError, httpx.ReadTimeout) as e:
        pytest.skip(f"Got expected error: {e}")



@pytest.mark.asyncio
async def test_get_balance(network):
    from secret import mnemo
    account = DagAccount()
    account.login_with_seed_phrase(mnemo)
    assert account.address == "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX"
    try:
        r = await account.get_balance()
        assert r == 0
        metagraph_account = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
            l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
            cl1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200"
        )
        r = await metagraph_account.get_balance()
        assert r >= 0
    except (httpx.ReadTimeout, NetworkError) as e:
        pytest.skip(f"Error: {e}")

@pytest.mark.asyncio
async def test_get_currency_transactions(network):
    from secret import mnemo
    account = DagAccount()
    account.login_with_seed_phrase(mnemo)
    metagraph_account = MetagraphTokenClient(
        account=account,
        metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
        cl1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200"
    )
    r = await metagraph_account.get_transactions(limit=3)
    assert len(r) == 3

@pytest.mark.asyncio
async def test_currency_transfer(network):
    from secret import mnemo, to_address
    account = DagAccount()
    account.login_with_seed_phrase(mnemo)
    account.connect(network_id='testnet')
    failed = []
    try:
        r = await account.transfer(to_address=to_address, amount=100000000, fee=200000)
        assert isinstance(r, PendingTransaction)
    except (NetworkError, httpx.ReadError) as e:
        failed.append(e)

    metagraph_account = MetagraphTokenClient(
        account=account,
        metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        # l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
        cl1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200"
    )

    try:
        r = await metagraph_account.transfer(to_address=to_address, amount=10000000, fee=2000000)
        assert isinstance(r, dict)
    except (NetworkError, httpx.ReadTimeout) as e:
        failed.append(e)

    if failed:
        pytest.skip(', '.join(str(x) for x in failed))

@pytest.mark.asyncio
async def test_currency_batch_transfer(network):
    from secret import mnemo, to_address
    from pypergraph.account import DagAccount
    account = DagAccount()
    account.login_with_seed_phrase(mnemo)
    account.connect(network_id='integrationnet')
    # last_ref = await account.network.get_address_last_accepted_transaction_ref(account.address)

    txn_data = [
        {'to_address': to_address, 'amount': 10000000, 'fee': 200000},
        {'to_address': to_address, 'amount': 5000000, 'fee': 200000},
        {'to_address': to_address, 'amount': 2500000, 'fee': 200000},
        {'to_address': to_address, 'amount': 1, 'fee': 200000}
    ]
    try:
        r = await account.transfer_dag_batch(transfers=txn_data)
        assert len(r) == 4
    except (NetworkError, httpx.ReadTimeout) as e:
        pytest.skip(f"Got expected error: {e}")
    """PACA Metagraph doesn't function well with bulk transfers, it seems"""
    # metagraph_account = MetagraphTokenClient(
    #     account=account,
    #     metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
    #     l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
    #     cl1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200"
    # )
    # last_ref = await metagraph_account.network.get_address_last_accepted_transaction_ref(account.address)
    # r = await metagraph_account.transfer_batch(transfers=txn_data)
    # assert len(r) == 4
