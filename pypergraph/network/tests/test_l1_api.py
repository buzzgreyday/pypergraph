import re
from ipaddress import IPv4Network

import httpx
import pytest
from pytest_httpx import HTTPXMock

from .conf import mock_l1_api_responses, network, l1_transaction_error_msgs
from pypergraph.account import DagAccount, MetagraphTokenClient
from .secret import mnemo, to_address
from ...core.exceptions import NetworkError


@pytest.mark.mock
class TestMockedL1API:

    @pytest.mark.asyncio
    async def test_get_l1_cluster_info(self, network, httpx_mock: HTTPXMock, mock_l1_api_responses):
        network.config("integrationnet")
        httpx_mock.add_response(url="https://l1-lb-integrationnet.constellationnetwork.io/cluster/info",
                                json=mock_l1_api_responses["cluster_info"])
        results = await network.cl1_api.get_cluster_info()
        assert [r.model_dump() for r in results] == [{'alias': None, 'id': '615b72d69facdbd915b234771cd4ffe49692a573f7ac05fd212701afe9b703eb8ab2ab117961f819e6d5eaf5ad073456cf56a0422c67b17606d95f50460a919d', 'ip': IPv4Network('5.161.233.213/32'), 'state': 'Ready', 'session': 1748983955866, 'public_port': 9000, 'p2p_port': 9001, 'reputation': None}]

    @pytest.mark.asyncio
    async def test_get_last_ref(self, network, httpx_mock: HTTPXMock, mock_l1_api_responses):
        network.config("integrationnet")
        address = "DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw"
        httpx_mock.add_response(url="https://l1-lb-integrationnet.constellationnetwork.io/transactions/last-reference/DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw",
                                json=mock_l1_api_responses["last_ref"])
        result = await network.get_address_last_accepted_transaction_ref(address)
        assert result.model_dump() == {'ordinal': 0, 'hash': '0000000000000000000000000000000000000000000000000000000000000000'}

    @pytest.mark.asyncio
    async def test_get_not_pending(self, network, httpx_mock: HTTPXMock, mock_l1_api_responses):
        # TODO: This might be deprecated
        network.config("integrationnet")
        httpx_mock.add_response(status_code=404,
                                url="https://l1-lb-integrationnet.constellationnetwork.io/transactions/fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429")
        result = await network.get_pending_transaction(
            hash="fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429"
        )
        assert not result # This transaction isn't pending.

    @pytest.mark.asyncio
    async def test_post_transaction_success(self, network, httpx_mock: HTTPXMock, mock_l1_api_responses):
        network.config("integrationnet")
        httpx_mock.add_response(
            url="https://l1-lb-integrationnet.constellationnetwork.io/transactions/last-reference/DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
            json=mock_l1_api_responses["last_ref"])
        account = DagAccount()
        account.connect(network_id="integrationnet")
        account.login_with_seed_phrase(mnemo)
        tx, hash_ = await account.generate_signed_transaction(
            to_address=to_address, amount=100000000, fee=200000000
        )
        httpx_mock.add_response(
            method="POST",
            url="https://l1-lb-integrationnet.constellationnetwork.io/transactions",  # adjust if needed
            json=mock_l1_api_responses["post_transaction"],
            status_code=200
        )
        await account.network.post_transaction(tx)

    @pytest.mark.asyncio
    async def test_post_metagraph_currency_transaction(self, network, httpx_mock: HTTPXMock, mock_l1_api_responses):
        from .secret import mnemo, to_address, from_address

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account_metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
            l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
            currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200",
        )
        httpx_mock.add_response(
            url="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200/transactions/last-reference/DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX",
            json=mock_l1_api_responses["last_ref"])
        # Generate signed tx
        last_ref = await account_metagraph_client.network.get_address_last_accepted_transaction_ref(
            address=from_address
        )
        tx, hash_ = await account_metagraph_client.account.generate_signed_transaction(
            to_address=to_address, amount=10000000, fee=2000000, last_ref=last_ref
        )
        httpx_mock.add_response(
            method="POST",
            url="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200/transactions",  # adjust if needed
            json=mock_l1_api_responses["post_transaction"],
            status_code=200
        )
        await account_metagraph_client.network.post_transaction(tx=tx)


@pytest.mark.integration
class TestIntegrationL1API:

    @pytest.mark.asyncio
    async def test_get_l1_cluster_info(self, network):
        network.config("integrationnet")
        results = await network.cl1_api.get_cluster_info()
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_get_last_ref(self, network):
        network.config("integrationnet")
        address = "DAG7XAG6oteEfCpwuGyZVb9NDSh2ue9kmoe26cmw"
        result = await network.get_address_last_accepted_transaction_ref(address)
        assert result.ordinal >= 0 and isinstance(result.hash, str)

    @pytest.mark.asyncio
    async def test_get_pending(self, network):
        # TODO: This might be deprecated
        network.config("integrationnet")
        result = await network.get_pending_transaction(
            hash="fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429"
        )
        assert not result # This transaction isn't pending.

    @pytest.mark.asyncio
    async def test_post_transaction(self, network, l1_transaction_error_msgs):

        account = DagAccount()
        account.connect(network_id="integrationnet")
        account.login_with_seed_phrase(mnemo)
        tx, hash_ = await account.generate_signed_transaction(
            to_address=to_address, amount=10000000, fee=200000000
        )

        try:
            response = await account.network.post_transaction(tx)
            assert bool(re.fullmatch(r"[a-fA-F0-9]{64}", response))
        except NetworkError as e:
            for error, description in l1_transaction_error_msgs.items():
                if error in str(e):
                    pytest.skip(f"Skipping due to expected error '{error}': {description}")
            raise

    @pytest.mark.asyncio
    async def test_post_metagraph_currency_transaction(self, network, l1_transaction_error_msgs):
        from .secret import mnemo, to_address, from_address

        account = DagAccount()
        account.login_with_seed_phrase(mnemo)
        account_metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
            l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100",
            currency_l1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200",
        )
        try:
            # Generate signed tx
            last_ref = await account_metagraph_client.network.get_address_last_accepted_transaction_ref(
                address=from_address
            )
            tx, hash_ = await account_metagraph_client.account.generate_signed_transaction(
                to_address=to_address, amount=10000000, fee=2000000, last_ref=last_ref
            )
            await account_metagraph_client.network.post_transaction(tx=tx)
        except (NetworkError, httpx.ReadError) as e:
            for error, description in l1_transaction_error_msgs.items():
                if error in str(e):
                    pytest.skip(f"Skipping due to expected error '{error}': {description}")
            raise
        except httpx.ReadTimeout:
            pytest.skip("Skipping due to timeout")
        except httpx.ReadError:
            pytest.skip("Did not receive any data from the network.")