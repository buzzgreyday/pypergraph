import httpx
import pytest
from pytest_httpx import HTTPXMock

from pypergraph.core.exceptions import NetworkError
from pypergraph.account import DagAccount, MetagraphTokenClient
from pypergraph.network.models.transaction import PendingTransaction


@pytest.mark.account
class TestAccount:
    @pytest.mark.asyncio
    async def test_dag_account_connect(self):
        """Configure the network connection."""
        account = DagAccount()
        account.connect(network_id="testnet")
        assert account.network.get_network() == {
            "data_l1_host": None,
            "network_id": "testnet",
            "block_explorer_url": "https://be-testnet.constellationnetwork.io",
            "l0_host": "https://l0-lb-testnet.constellationnetwork.io",
            "currency_l1_host": "https://l1-lb-testnet.constellationnetwork.io",
            "metagraph_id": None,
        }
        account.connect(network_id="integrationnet")
        assert account.network.get_network() == {
            "data_l1_host": None,
            "network_id": "integrationnet",
            "block_explorer_url": "https://be-integrationnet.constellationnetwork.io",
            "l0_host": "https://l0-lb-integrationnet.constellationnetwork.io",
            "currency_l1_host": "https://l1-lb-integrationnet.constellationnetwork.io",
            "metagraph_id": None,
        }
        account.connect(network_id="mainnet")
        assert account.network.get_network() == {
            "data_l1_host": None,
            "network_id": "mainnet",
            "block_explorer_url": "https://be-mainnet.constellationnetwork.io",
            "l0_host": "https://l0-lb-mainnet.constellationnetwork.io",
            "currency_l1_host": "https://l1-lb-mainnet.constellationnetwork.io",
            "metagraph_id": None,
        }
        account.connect(
            network_id="mainnet",
            l0_host="http://123.123.13.123:9000",
            cl1_host="http://123.123.123.123:9010",
        )
        assert account.network.get_network() == {
            "data_l1_host": None,
            "network_id": "mainnet",
            "block_explorer_url": "https://be-mainnet.constellationnetwork.io",
            "l0_host": "http://123.123.13.123:9000",
            "currency_l1_host": "http://123.123.123.123:9010",
            "metagraph_id": None,
        }

    @pytest.mark.asyncio
    async def test_metagraph_account_connect(self):
        """
        account.network_id is either ethereum or constellation, account.network.network_id is either mainnet,
        integrationnet or testnet. Lb should get reset and be_url should be set as
        get_currency_transactions by address is using BE
        :return:
        """
        from secret import mnemo

        account = DagAccount()
        account.connect(network_id="testnet")
        account.login_with_seed_phrase(mnemo)
        metagraph = MetagraphTokenClient(
            account=account,
            l0_host="http://123.123.123.123:9000",
            data_l1_host="http://123.123.123.123:9020",
            currency_l1_host="http://123.123.123.123:9010",
            metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        )
        metagraph.network.get_network()
        assert metagraph.network.get_network() == {
            "data_l1_host": "http://123.123.123.123:9020",
            "network_id": "testnet",
            "block_explorer_url": "https://be-testnet.constellationnetwork.io",
            "l0_host": "http://123.123.123.123:9000",
            "currency_l1_host": "http://123.123.123.123:9010",
            "metagraph_id": "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        }
        metagraph = account.create_metagraph_token_client(
            metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
            currency_l1_host="http://123.123.123.123:9010",
        )
        assert metagraph.network.get_network() == {
            "data_l1_host": None,
            "network_id": "testnet",
            "block_explorer_url": "https://be-testnet.constellationnetwork.io",
            "l0_host": "https://l0-lb-testnet.constellationnetwork.io",
            "currency_l1_host": "http://123.123.123.123:9010",
            "metagraph_id": "DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        }
        try:
            await metagraph.get_balance()
        except httpx.ReadTimeout as e:
            pytest.skip(f"Got expected error: {e}")

    @pytest.mark.asyncio
    async def test_login_logout(self):
        from secret import mnemo

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        private_key = account.private_key
        assert (
            account.key_trio.public_key
            == "044462191fb1056699c28607c7e8e03b73602fa070b78cad863b5f84d08a577d5d0399ccd90ba1e69f34382d678216d4b2a030d98e38c0c960447dc49514f92ad7"
        )
        assert (
            account.key_trio.private_key
            == "18e19114377f0b4ae5b9426105ffa4d18c791f738374b5867ebea836e5722710"
        )
        assert account.key_trio.address == "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX"
        account.logout()
        account.login_with_private_key(private_key)
        public_key = account.public_key
        assert (
            account.key_trio.public_key
            == "044462191fb1056699c28607c7e8e03b73602fa070b78cad863b5f84d08a577d5d0399ccd90ba1e69f34382d678216d4b2a030d98e38c0c960447dc49514f92ad7"
        )
        assert (
            account.key_trio.private_key
            == "18e19114377f0b4ae5b9426105ffa4d18c791f738374b5867ebea836e5722710"
        )
        assert account.key_trio.address == "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX"
        account.logout()
        account.login_with_public_key(public_key)
        assert (
            account.key_trio.public_key
            == "044462191fb1056699c28607c7e8e03b73602fa070b78cad863b5f84d08a577d5d0399ccd90ba1e69f34382d678216d4b2a030d98e38c0c960447dc49514f92ad7"
        )
        assert not account.key_trio.private_key
        assert account.key_trio.address == "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX"
        account.logout()


@pytest.mark.mock
class TestMockAccount:
    @pytest.mark.asyncio
    async def test_get_balance(
        self,
        dag_account,
        metagraph_account,
        httpx_mock: HTTPXMock,
        mock_shared_responses,
    ):
        assert dag_account.address == "DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX"
        httpx_mock.add_response(
            url="https://l0-lb-mainnet.constellationnetwork.io/dag/DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX/balance",
            json=mock_shared_responses["balance"],
        )
        r = await dag_account.get_balance()
        assert r == 218000000
        httpx_mock.add_response(
            url="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100/currency/DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX/balance",
            json=mock_shared_responses["balance"],
        )
        r = await metagraph_account.get_balance()
        assert r == 218000000

    @pytest.mark.asyncio
    async def test_get_currency_transactions(
        self, metagraph_account, httpx_mock: HTTPXMock, mock_block_explorer_responses
    ):
        httpx_mock.add_response(
            url="https://be-mainnet.constellationnetwork.io/currency/DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43/addresses/DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX/transactions?limit=3",
            json=mock_block_explorer_responses["transactions_limit_3"],
        )
        r = await metagraph_account.get_transactions(limit=3)
        assert len(r) == 3

    @pytest.mark.asyncio
    async def test_currency_transfer(
        self,
        dag_account,
        metagraph_account,
        httpx_mock: HTTPXMock,
        mock_l1_api_responses,
    ):
        from secret import to_address

        dag_account.connect(network_id="integrationnet")
        httpx_mock.add_response(
            method="GET",
            url="https://l1-lb-integrationnet.constellationnetwork.io/transactions/last-reference/DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
            json=mock_l1_api_responses["last_ref"],
        )
        httpx_mock.add_response(
            method="POST",
            url="https://l1-lb-integrationnet.constellationnetwork.io/transactions",  # adjust if needed
            json={
                "data": {
                    "hash": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
                }
            },
            status_code=200,
        )

        r = await dag_account.transfer(
            to_address=to_address, amount=100000000, fee=200000
        )

        assert isinstance(r, PendingTransaction)

        httpx_mock.add_response(
            method="GET",
            url="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200/transactions/last-reference/DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
            json=mock_l1_api_responses["last_ref"],
        )
        httpx_mock.add_response(
            method="POST",
            url="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200/transactions",  # adjust if needed
            json={
                "data": {
                    "hash": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
                }
            },
            status_code=200,
        )

        r = await metagraph_account.transfer(
            to_address=to_address, amount=10000000, fee=2000000
        )
        assert isinstance(r, dict)

    @pytest.mark.asyncio
    async def test_currency_batch_transfer(
        self,
        dag_account,
        metagraph_account,
        httpx_mock: HTTPXMock,
        mock_l1_api_responses,
    ):
        # TODO: Mock this
        from secret import to_address

        dag_account.connect(network_id="integrationnet")
        # last_ref = await account.network.get_address_last_accepted_transaction_ref(account.address)

        txn_data = [
            {"to_address": to_address, "amount": 10000000, "fee": 200000},
            {"to_address": to_address, "amount": 5000000, "fee": 200000},
            {"to_address": to_address, "amount": 2500000, "fee": 200000},
            {"to_address": to_address, "amount": 1, "fee": 200000},
        ]

        httpx_mock.add_response(
            method="GET",
            url="https://l1-lb-integrationnet.constellationnetwork.io/transactions/last-reference/DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
            json=mock_l1_api_responses["last_ref"],
        )
        for _ in range(len(txn_data)):
            httpx_mock.add_response(
                method="POST",
                url="https://l1-lb-integrationnet.constellationnetwork.io/transactions",
                json={
                    "data": {
                        "hash": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
                    }
                },
                status_code=200,
            )
        try:
            r = await dag_account.transfer_batch(transfers=txn_data)
            assert len(r) == 4
        except (NetworkError, httpx.ReadTimeout) as e:
            pytest.skip(f"Got expected error: {e}")
        """PACA Metagraph doesn't function well with bulk transfers, it seems"""
        # metagraph_account = MetagraphTokenClient(
        #     account=account,
        #     metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        #     l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
        #     currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200"
        # )
        # last_ref = await metagraph_account.network.get_address_last_accepted_transaction_ref(account.address)
        # r = await metagraph_account.transfer_batch(transfers=txn_data)
        # assert len(r) == 4


@pytest.mark.integration
class TestIntegrationAccount:
    @pytest.mark.asyncio
    async def test_get_balance(self):
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
                currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200",
            )
            r = await metagraph_account.get_balance()
            assert r >= 0
        except (httpx.ReadTimeout, NetworkError) as e:
            pytest.skip(f"Error: {e}")

    @pytest.mark.asyncio
    async def test_get_currency_transactions(self):
        from secret import mnemo

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        metagraph_account = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
            l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
            currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200",
        )
        r = await metagraph_account.get_transactions(limit=3)
        assert len(r) == 3

    @pytest.mark.asyncio
    async def test_currency_transfer(self):
        from secret import mnemo, to_address

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account.connect(network_id="integrationnet")
        failed = []
        try:
            r = await account.transfer(
                to_address=to_address, amount=100000000, fee=200000
            )
            assert isinstance(r, PendingTransaction)
        except (NetworkError, httpx.ReadError):
            failed.append("Integrationnet DAG: Network error or Httpx read error.")
        except httpx.ReadTimeout:
            failed.append("Integrationnet DAG: Timeout Error")

        metagraph_account = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
            # l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
            currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200",
        )

        try:
            r = await metagraph_account.transfer(
                to_address=to_address, amount=10000000, fee=2000000
            )
            assert isinstance(r, dict)
        except (NetworkError, httpx.ReadError):
            failed.append("El Paca Metagraph: Network or HTTPX ReadError (timeout)")

        if failed:
            pytest.skip(", ".join(str(x) for x in failed))

    @pytest.mark.asyncio
    async def test_currency_batch_transfer(self):
        from secret import mnemo, to_address
        from pypergraph.account import DagAccount

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account.connect(network_id="integrationnet")
        # last_ref = await account.network.get_address_last_accepted_transaction_ref(account.address)

        txn_data = [
            {"to_address": to_address, "amount": 10000000, "fee": 200000},
            {"to_address": to_address, "amount": 5000000, "fee": 200000},
            {"to_address": to_address, "amount": 2500000, "fee": 200000},
            {"to_address": to_address, "amount": 1, "fee": 200000},
        ]
        try:
            r = await account.transfer_batch(transfers=txn_data)
            assert len(r) == 4
        except (NetworkError, httpx.ReadTimeout) as e:
            pytest.skip(f"Got expected error: {e}")
        """PACA Metagraph doesn't function well with bulk transfers, it seems"""
        # metagraph_account = MetagraphTokenClient(
        #     account=account,
        #     metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
        #     l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
        #     currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200"
        # )
        # last_ref = await metagraph_account.network.get_address_last_accepted_transaction_ref(account.address)
        # r = await metagraph_account.transfer_batch(transfers=txn_data)
        # assert len(r) == 4

    @pytest.mark.asyncio
    async def test_token_lock(self):
        from secret import mnemo
        from pypergraph.account import DagAccount

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account.connect(network_id="integrationnet")

        # latest_snapshot = await account.network.l0_api.get_latest_snapshot()
        # latest_epoch = latest_snapshot.value.epoch_progress
        try:
            res = await account.create_token_lock(500000000000)
        except NetworkError as e:
            pytest.skip("Got expected error: " + e.message)
        assert res.get("hash")

    @pytest.mark.asyncio
    async def test_allow_spend(self):
        """Receives status 500"""
        # TODO: Mock this
        from secret import mnemo
        from pypergraph.account import DagAccount

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account.connect(network_id="integrationnet")

        latest_snapshot = await account.network.l0_api.get_latest_snapshot()
        latest_epoch = latest_snapshot.value.epoch_progress
        try:
            res = await account.create_allow_spend(
                destination="DAG1GH7r7RX1Ca7MbuvqUPT37FAtTfGM1WYQ4otZ",
                amount=10000000000,
                approvers=["DAG1GH7r7RX1Ca7MbuvqUPT37FAtTfGM1WYQ4otZ"],
                valid_until_epoch=latest_epoch + 10,
            )
            assert res == res.get("hash")
        except NetworkError:
            pytest.skip("Expecting status 500.")
