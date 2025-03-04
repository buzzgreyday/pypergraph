import pytest

from pypergraph.dag_network import DagTokenNetwork
from pypergraph.dag_account import DagAccount, MetagraphTokenClient


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
    account = DagAccount()
    account.connect(network_id='testnet')
    metagraph_account = MetagraphTokenClient(account=account, l0_host='http://123.123.123.123:9000', dl1_host='http://123.123.123.123:9020', cl1_host='http://123.123.123.123:9010', metagraph_id='DAG6DOES00NOT00MATTER00HERE')
    metagraph_account.network.get_network()
    assert metagraph_account.network.get_network() == {
        'dl1_host': 'http://123.123.123.123:9020',
        'network_id': 'constellation',
        'be_url': 'https://be-testnet.constellationnetwork.io',
        'l0_lb_url': None,
        'l1_lb_url': None,
        'l0_host': 'http://123.123.123.123:9000',
        'cl1_host': 'http://123.123.123.123:9010',
        'metagraph_id': 'DAG6DOES00NOT00MATTER00HERE'
    }

@pytest.mark.asyncio
async def test_get_balance(network):
    from secrets import mnemo
    account = DagAccount()
    account.login_with_seed_phrase(mnemo)
    assert account.address == "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX"
    r = await account.get_balance()
    assert r == 0
    metagraph_account = MetagraphTokenClient(
        account=account,
        metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
        cl1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200"
    )
    r = await metagraph_account.get_balance()
    assert r in (0, 100000000)