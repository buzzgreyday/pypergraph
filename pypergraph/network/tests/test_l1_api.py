from ipaddress import IPv4Network

import pytest
from pytest_httpx import HTTPXMock

from .conf import mock_l1_api_responses, network

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
        network.config("integrationnet")
        httpx_mock.add_response(status_code=404,
                                url="https://l1-lb-integrationnet.constellationnetwork.io/transactions/fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429")
        result = await network.get_pending_transaction(
            hash="fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429"
        )
        assert not result # This transaction isn't pending.


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
        network.config("integrationnet")
        result = await network.get_pending_transaction(
            hash="fdac1db7957afa1277937e2c7a98ad55c5c3bb456f558d69f2af8e01dac29429"
        )
        assert not result # This transaction isn't pending.

