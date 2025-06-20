import pytest

from pypergraph import MetagraphTokenClient
from pypergraph.account import DagAccount


@pytest.fixture
def dag_account():
    from secret import mnemo

    dag_account = DagAccount()
    dag_account.login_with_seed_phrase(mnemo)
    return dag_account


@pytest.fixture
def metagraph_account():
    from secret import mnemo

    dag_account = DagAccount()
    dag_account.login_with_seed_phrase(mnemo)
    metagraph_account = MetagraphTokenClient(
        account=dag_account,
        metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
        currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200",
    )
    return metagraph_account


@pytest.fixture
def mock_shared_responses():
    return {"balance": {"ordinal": 4493725, "balance": 218000000}}

