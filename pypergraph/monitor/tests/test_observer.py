import pytest
from rx.testing import TestScheduler, ReactiveTest

from pypergraph.account import DagAccount
from pypergraph.keyring import KeyringManager
from pypergraph.monitor.tests import secret
from pypergraph.network import DagTokenNetwork


@pytest.mark.asyncio
async def test_login():
    def test_handle_session_change(session_changed):
        assert session_changed
    # Create account and monitor session changes
    account = DagAccount()
    account.observe_session_change().subscribe(
        test_handle_session_change
    )

    # Login and perform operations
    account.login_with_seed_phrase(words=secret.mnemo)

@pytest.mark.asyncio
async def test_network_change():

    network = DagTokenNetwork()
    async def test_handle_net_change(network_change):
        assert network_change == {
            'dl1_host': None,
            'network_id': 'testnet',
            'be_url': 'https://be-testnet.constellationnetwork.io',
            'l0_lb_url': 'https://l0-lb-testnet.constellationnetwork.io',
            'l1_lb_url': 'https://l1-lb-testnet.constellationnetwork.io',
            'l0_host': 'https://l0-lb-testnet.constellationnetwork.io',
            'cl1_host': 'https://l1-lb-testnet.constellationnetwork.io',
            'metagraph_id': None
        }

    # Subscribe to network changes (async-aware)
    network.observe_network_change().subscribe(
        on_next=test_handle_net_change,
        on_error=lambda e: print(f"Error: {e}")
    )

    network.config("testnet")
    with pytest.raises(ValueError, match="Invalid network id"):
        network.config("shoe_polish")


def test_async_network_change():
    scheduler = TestScheduler()
    # Inject the test scheduler so the observable emits on virtual time.
    network = DagTokenNetwork(scheduler=scheduler)
    observer = scheduler.create_observer()

    network.observe_network_change().subscribe(observer)

    # Schedule the config change at virtual time 100.
    def test_actions(scheduler, state):
        network.config('testnet')

    scheduler.schedule_absolute(100, test_actions)
    scheduler.start()

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
        ReactiveTest.on_next(100, expected_config),
    ]

@pytest.mark.asyncio
async def test_async_manager_observer():
    # Subscribe to network changes (async-aware)
    manager = KeyringManager()
    manager._on_state_change.subscribe(
        on_next=lambda e: print(f"State change: {e}"),
        on_error=lambda e: print(f"Error: {e}")
    )

    await manager.login(password="super_S3cretP_Asswo0rd")