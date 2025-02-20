import pytest

from pypergraph.dag_keyring import KeyringManager
from pypergraph.dag_keyring.tests.secrets import mnemo, from_address


@pytest.fixture
def key_manager():
    return KeyringManager()

@pytest.mark.asyncio
async def test_create_or_restore_wallet(key_manager):
    await key_manager.create_or_restore_vault(password="super_S3cretP_Asswo0rd", seed=mnemo)
    account = key_manager.get_wallet_for_account(from_address)
    print(account)

@pytest.mark.asyncio
async def test_create_hd_wallet(key_manager):
    key_manager.set_password("super_S3cretP_Asswo0rd")
    await key_manager.create_multi_chain_hd_wallet(seed=mnemo)
    account = key_manager.get_wallet_for_account(from_address)
    await key_manager.create_multi_chain_hd_wallet(seed=mnemo)
    print(key_manager.wallets)
