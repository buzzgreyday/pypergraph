"""Unit tests for network configuration - no external dependencies"""

import pytest
from pypergraph.network import DagTokenNetwork
from pypergraph.network.models.network import NetworkInfo


class TestNetworkConfiguration:
    """Test network configuration without external calls"""

    @pytest.mark.parametrize(
        "network_id, expected",
        [
            (
                "testnet",
                NetworkInfo(
                    network_id="testnet",
                    block_explorer_url="https://be-testnet.constellationnetwork.io",
                    l0_host="https://l0-lb-testnet.constellationnetwork.io",
                    currency_l1_host="https://l1-lb-testnet.constellationnetwork.io",
                ),
            ),
            (
                "integrationnet",
                NetworkInfo(
                    network_id="integrationnet",
                    block_explorer_url="https://be-integrationnet.constellationnetwork.io",
                    l0_host="https://l0-lb-integrationnet.constellationnetwork.io",
                    currency_l1_host="https://l1-lb-integrationnet.constellationnetwork.io",
                ),
            ),
            (
                "mainnet",
                NetworkInfo(
                    network_id="mainnet",
                    block_explorer_url="https://be-mainnet.constellationnetwork.io",
                    l0_host="https://l0-lb-mainnet.constellationnetwork.io",
                    currency_l1_host="https://l1-lb-mainnet.constellationnetwork.io",
                ),
            ),
            (
                None,
                NetworkInfo(
                    network_id="mainnet",
                    block_explorer_url="https://be-mainnet.constellationnetwork.io",
                    l0_host="https://l0-lb-mainnet.constellationnetwork.io",
                    currency_l1_host="https://l1-lb-mainnet.constellationnetwork.io",
                ),
            ),
        ],
    )
    def test_init_network(self, network_id, expected):
        """Test network initialization with different network IDs"""
        net = DagTokenNetwork(network_id) if network_id else DagTokenNetwork()
        assert net.get_network() == expected.__dict__

    def test_custom_network_initialization(self):
        """Test custom network host initialization"""
        custom_l0_host = "http://custom-l0:9000"
        custom_l1_host = "http://custom-l1:9200"

        net = DagTokenNetwork(
            network_id="mainnet",
            l0_host=custom_l0_host,
            currency_l1_host=custom_l1_host,
        )
        assert net.get_network() == {
            "data_l1_host": None,
            "network_id": "mainnet",
            "block_explorer_url": "https://be-mainnet.constellationnetwork.io",
            "l0_host": "http://custom-l0:9000",
            "currency_l1_host": "http://custom-l1:9200",
            "metagraph_id": None,
        }
