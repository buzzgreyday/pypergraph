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
async def test_async_manager_observers():
    # Subscribe to network changes (async-aware)
    def event_handler(event):
        if event["type"] == "lock":
            print("Vault locked!")
        elif event["type"] == "unlock":
            print("Vault unlocked!")
        elif event["type"] == "account_update":
            print("Account updated:", event["data"])
        elif event["type"] == "removed_account":
            print("Account removed:", event["data"])
        elif event["type"] == "state_update":
            print("State updated:", event["data"])
    manager = KeyringManager()
    manager.observe_account_change.subscribe(event_handler)
    manager.observe_state_change.subscribe(
        on_next=lambda state: print(f"State changed: {state}",
                                    )
    )

    # First we "create" a new wallet
    await manager.create_or_restore_vault("super_S3cretP_Asswo0rd", "New Wallet", secret.mnemo)
    # Then login as we would after creating the storage file (can be used without above step when file is present)
    await manager.login(password="super_S3cretP_Asswo0rd")
    # We then logout
    await manager.logout()

from rx import of
from rx import operators as ops

def test_safe_divide():

    def safe_divide(x):
        try:
            return x / (x - 3)
        except Exception as e:
            print(f"Error processing value {x}: {e}")
            return None  # or any fallback value, or skip it

    source = of(1, 2, 3, 4, 5).pipe(
        ops.map(safe_divide),
        ops.filter(lambda result: result is not None)  # Optionally filter out fallback values
    )

    source.subscribe(
        on_next=lambda x: print(f"Received: {x}"),
        on_error=lambda e: print(f"Error: {e}"),
        on_completed=lambda: print("Completed")
)
