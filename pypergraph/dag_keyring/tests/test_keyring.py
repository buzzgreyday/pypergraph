import pytest

from pypergraph.dag_keyring import KeyringManager
from pypergraph.dag_keyring.tests.secrets import mnemo, from_address
from pypergraph.dag_keystore import KeyStore


@pytest.fixture
def key_manager():
    return KeyringManager()

@pytest.mark.asyncio
async def test_create_or_restore_wallet(key_manager):
    wallet = await key_manager.create_or_restore_vault(password="super_S3cretP_Asswo0rd", seed=mnemo)
    assert wallet.model_dump() == {
        'type': 'MCW',
        'label': 'Wallet #1',
        'secret': 'multiply angle perfect verify behind sibling skirt attract first lift remove fortune',
        'rings': [
            {
                'network': 'Constellation',
                'accounts': [
                    {
                        'bip44_index': 0
                    }
                ]
            },
            {
                'network': 'Ethereum',
                'accounts': [
                    {
                        'tokens': [
                            '0xa393473d64d2F9F026B60b6Df7859A689715d092'
                        ],
                        'bip44_index': 0
                    }
                ]
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_hd_wallet(key_manager):
    key_manager.set_password("super_S3cretP_Asswo0rd")
    wallet = await key_manager.create_multi_chain_hd_wallet(seed=mnemo)
    assert wallet.model_dump() == {
        'type': 'MCW',
        'label': 'Wallet #1',
        'secret': 'multiply angle perfect verify behind sibling skirt attract first lift remove fortune',
        'rings': [
            {
                'network': 'Constellation',
                'accounts': [
                    {
                        'bip44_index': 0
                    }
                ]
            },
            {
                'network': 'Ethereum',
                'accounts': [
                    {
                        'tokens': [
                            '0xa393473d64d2F9F026B60b6Df7859A689715d092'
                        ],
                        'bip44_index': 0
                    }
                ]
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_single_account_wallet(key_manager):
    key_manager.set_password("super_S3cretP_Asswo0rd")
    pk = KeyStore.get_private_key_from_mnemonic(mnemo)
    wallet = await key_manager.create_single_account_wallet(label="New SAW", private_key=pk)
    assert wallet.model_dump() == {
        'type': 'SAW',
        'label': 'New SAW',
        'network': 'Constellation',
        'secret': '18e19114377f0b4ae5b9426105ffa4d18c791f738374b5867ebea836e5722710'
    }


@pytest.mark.asyncio
async def test_create_wallet_ids(key_manager):
    key_manager.set_password("super_S3cretP_Asswo0rd")
    pk = KeyStore.get_private_key_from_mnemonic(mnemo)
    await key_manager.create_single_account_wallet(label="New SAW", private_key=pk)
    await key_manager.create_multi_chain_hd_wallet(seed=mnemo)
    assert [wallet.id for wallet in key_manager.wallets] == ['SAW1', 'MCW2']

@pytest.mark.asyncio
async def test_manager_login(key_manager):
    await key_manager.login("super_S3cretP_Asswo0rd")
    assert [wallet.model_dump() for wallet in key_manager.wallets] == [{'type': 'SAW', 'label': 'New SAW', 'network': 'Constellation', 'secret': '18e19114377f0b4ae5b9426105ffa4d18c791f738374b5867ebea836e5722710'}, {'type': 'MCW', 'label': 'Wallet #2', 'secret': 'multiply angle perfect verify behind sibling skirt attract first lift remove fortune', 'rings': [{'network': 'Constellation', 'accounts': [{'bip44_index': 0}]}, {'network': 'Ethereum', 'accounts': [{'tokens': ['0xa393473d64d2F9F026B60b6Df7859A689715d092'], 'bip44_index': 0}]}]}]
