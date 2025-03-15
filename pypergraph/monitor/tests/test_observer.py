import pytest
from rx.testing import TestScheduler, ReactiveTest
from pypergraph.account import DagAccount
from pypergraph.monitor.tests import secret
from pypergraph.network import DagTokenNetwork


@pytest.mark.asyncio
async def test_login():
    # Create a test scheduler
    scheduler = TestScheduler()

    # Create account and mock observer
    account = DagAccount()
    observer = scheduler.create_observer()

    # Subscribe to session changes
    account.observe_session_change().subscribe(observer)

    # Define test actions
    def test_actions():
        account.login_with_seed_phrase(words=secret.mnemo)

    # Schedule the test actions
    scheduler.schedule_absolute(100, test_actions)

    # Run the test
    scheduler.start()

    # Verify the results
    assert observer.messages == [
        ReactiveTest.on_next(100, True)  # Session change on login
    ]


@pytest.mark.asyncio
async def test_network_change():
    # Create a test scheduler
    scheduler = TestScheduler()

    # Create network and mock observer
    network = DagTokenNetwork()
    observer = scheduler.create_observer()

    # Subscribe to network changes
    network.observe_network_change().subscribe(observer)

    # Define test actions
    def test_actions():
        # Valid config
        network.config('testnet')

        # Invalid config (should raise an error)
        with pytest.raises(ValueError):
            network.config('organic_chicken_soup')

    # Schedule the test actions
    scheduler.schedule_absolute(100, test_actions)

    # Run the test
    scheduler.start()

    # Verify the results
    expected_config = {
        'dl1_host': None,
        'network_id': 'testnet',
        'be_url': 'https://be-testnet.constellationnetwork.io',
        'l0_lb_url': 'https://l0-lb-testnet.constellationnetwork.io',
        'l1_lb_url': 'https://l1-lb-testnet.constellationnetwork.io',
        'l0_host': 'https://l0-lb-testnet.constellationnetwork.io',
        'cl1_host': 'https://l1-lb-testnet.constellationnetwork.io',
        'metagraph_id': None
    }

    assert observer.messages == [
        ReactiveTest.on_next(100, expected_config),  # Valid config
        ReactiveTest.on_error(100, ValueError)  # Invalid config raises error
    ]