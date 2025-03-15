import pytest
from pypergraph.account import DagAccount
from pypergraph.monitor.tests import secret
from pypergraph.network import DagTokenNetwork

### MAKE ASYNC !

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

def test_network_change():
    def test_hande_network_change(network_change):
        pass
        # Observe network changes
    network = DagTokenNetwork()
    network.observe_network_change().subscribe(
        on_next=lambda config: print(f"New config: {config}"),
        on_error=lambda e: print(f"Config error: {e}")
    )

    network.config('testnet')