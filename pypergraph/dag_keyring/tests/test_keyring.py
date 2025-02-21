import hashlib

import pytest
from ecdsa import SigningKey, SECP256k1

from pypergraph.dag_keyring import KeyringManager, MultiKeyWallet
from pypergraph.dag_keyring.bip import Bip39Helper, Bip32Helper
from pypergraph.dag_keyring.tests.secrets import mnemo, from_address
from pypergraph.dag_keystore import Bip39, KeyStore


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

@pytest.mark.asyncio
async def test_create_single_account_wallet(key_manager):
    key_manager.set_password("super_S3cretP_Asswo0rd")
    await key_manager.create_multi_chain_hd_wallet(seed=mnemo)
    key_manager.get_wallet_for_account(from_address)
    pk = KeyStore.get_private_key_from_mnemonic(mnemo)
    wallet = await key_manager.create_single_account_wallet(label="Super", private_key=pk)
    print(key_manager.wallets)

