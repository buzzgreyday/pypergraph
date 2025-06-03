import pytest

from pypergraph import DagAccount
from pypergraph.keyring import KeyringManager, MultiKeyWallet, MultiAccountWallet
from pypergraph.keyring.accounts.dag_asset_library import DagAssetLibrary
from pypergraph.keyring.models.kcs import KeyringAssetInfo
from pypergraph.keyring.tests.secret import mnemo, from_address
from pypergraph.keyring.tests.test_account import CustomAccount
from pypergraph.keystore import KeyStore

# We need to write some more tests

@pytest.fixture
def key_manager():
    return KeyringManager(storage_file_path="key_storage.json")

@pytest.mark.asyncio
async def test_create_or_restore_wallet(key_manager):
    wallet = await key_manager.create_or_restore_vault(password="super_S3cretP_Asswo0rd", seed=mnemo)
    assert wallet.id == "MCW1"
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
    assert wallet.id == "MCW2"


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
    assert wallet.id == "SAW3"
    await key_manager.logout() # Resets SID


@pytest.mark.asyncio
async def test_create_wallet_ids(key_manager):
    key_manager.set_password("super_S3cretP_Asswo0rd")
    pk = KeyStore.get_private_key_from_mnemonic(mnemo)
    await key_manager.create_single_account_wallet(label="New SAW", private_key=pk)
    await key_manager.create_multi_chain_hd_wallet(seed=mnemo)
    assert [wallet.id for wallet in key_manager.wallets] == ['SAW1', 'MCW2']
    await key_manager.logout()

@pytest.mark.asyncio
async def test_manager_login(key_manager):
    """Retrieves data from encryted json storage"""
    await key_manager.login("super_S3cretP_Asswo0rd")
    assert [wallet.model_dump() for wallet in key_manager.wallets] == [
        {
            'type': 'SAW',
            'label': 'New SAW',
            'network': 'Constellation',
            'secret': '18e19114377f0b4ae5b9426105ffa4d18c791f738374b5867ebea836e5722710'
        },
        {
            'type': 'MCW',
            'label': 'Wallet #2',
            'secret': 'multiply angle perfect verify behind sibling skirt attract first lift remove fortune',
            'rings': [
                {
                    'network': 'Constellation',
                    'accounts': [{'bip44_index': 0}]},
                {
                    'network': 'Ethereum',
                    'accounts': [
                        {'tokens': [
                            '0xa393473d64d2F9F026B60b6Df7859A689715d092'
                        ],
                            'bip44_index': 0
                        }
                    ]
                }
            ]
        }
    ]
    await key_manager.logout()

@pytest.mark.asyncio
async def test_add_tokens(key_manager):
    """Retrieves data from encryted json storage"""
    # TODO: Check Stargazer to see how this is used.
    dag_asset_library = DagAssetLibrary()
    await key_manager.login("super_S3cretP_Asswo0rd")
    token = KeyringAssetInfo(
        id='DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43',
        address='DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43',
        label='El Paca',
        symbol='PACA',
        network='mainnet',
        decimals=8
    )
    assert dag_asset_library.import_token(token)
    token = KeyringAssetInfo(
        id='DAG0CyySf35ftDQDQBnd1bdQ9aPyUdacMghpnCuM',
        address='DAG0CyySf35ftDQDQBnd1bdQ9aPyUdacMghpnCuM',
        label='Dor',
        symbol='DOR',
        network='mainnet',
        decimals=8
    )
    assert dag_asset_library.import_token(token)
    wallet = key_manager.get_wallet_for_account(from_address)
    w_state = wallet.get_state()
    w_network = wallet.get_network()
    w_label = wallet.get_label()
    assert w_state == {'id': 'SAW1', 'type': 'SAW', 'label': 'New SAW', 'supported_assets': ['DAG'], 'accounts': [{'address': 'DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX', 'network': 'Constellation', 'tokens': []}]}
    assert w_network == "Constellation"
    assert w_label == "New SAW"
    account = wallet.get_accounts()[0]
    account.set_tokens(dag_asset_library.imported_assets) # One would probably want to rely on different controllers for a wallet build
    assert account.get_state() == {'address': 'DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX', 'supported_assets': ['DAG'], 'tokens': {'PACA': {'id': 'DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43', 'label': 'El Paca', 'symbol': 'PACA', 'decimals': 8, 'native': None, 'network': 'mainnet', 'address': 'DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43'}, 'DOR': {'id': 'DAG0CyySf35ftDQDQBnd1bdQ9aPyUdacMghpnCuM', 'label': 'Dor', 'symbol': 'DOR', 'decimals': 8, 'native': None, 'network': 'mainnet', 'address': 'DAG0CyySf35ftDQDQBnd1bdQ9aPyUdacMghpnCuM'}}}


@pytest.mark.asyncio
async def test_create_multi_key_wallet(key_manager):
    """
    Can import pk but not export:
    Imports an account using the given secret and label, creates a keyring and adds it to the keyrings list.
    """
    pk = KeyStore.get_private_key_from_mnemonic(mnemo)
    wallet = MultiKeyWallet()
    wallet.create(network="Constellation", label="New MKW")
    wallet.import_account(private_key=pk, label="Keyring 1")
    wallet.import_account(private_key=pk, label="Keyring 2")
    assert wallet.get_state() == {'id': 'MKW3', 'type': 'MKW', 'label': 'New MKW', 'network': 'Constellation', 'supported_assets': ['DAG'], 'accounts': [{'address': 'DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX', 'label': 'Keyring 1'}, {'address': 'DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX', 'label': 'Keyring 2'}]}


@pytest.mark.asyncio
async def test_create_multi_account_wallet(key_manager):

    wallet = MultiAccountWallet()
    wallet.create(network="Constellation", label="New MAW", mnemonic=mnemo, num_of_accounts=3)
    assert wallet.get_state() == {
        'id': 'MAW4',
        'type': 'MAW',
        'label': 'New MAW',
        'supported_assets': ['DAG'],
        'accounts': [
            {
                'address': 'DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX',
                'supported_assets': ['DAG']
            },
            {
                'address': 'DAG0LX8bQXduupLy4SuCvQweTGDgYJG2aaBP4Ppq',
                'supported_assets': ['DAG']
            },
            {
                'address': 'DAG3LojBvdri3qytHBRRLaxMYUMzMdxXqkVEgGmn',
                'supported_assets': ['DAG']
            }
        ]
    }
    wallet.create(network="Ethereum", label="New MAW", mnemonic=mnemo, num_of_accounts=2)
    assert wallet.get_state() == {
        'id': 'MAW4',
        'type': 'MAW',
        'label': 'New MAW',
        'supported_assets': ['DAG', 'ETH', 'ERC20'],
        'accounts': [
            {
                'address': '0x8Fbc948ba2dD081A51036dE02582f5DcB51a310c',
                'supported_assets': ['ETH', 'ERC20'],
                'tokens': ['0xa393473d64d2F9F026B60b6Df7859A689715d092']
            },
            {
                'address': '0xA75E56eee5B790032316d8cd259DeBcf20E671BF',
                'supported_assets': ['ETH', 'ERC20'],
                'tokens': ['0xa393473d64d2F9F026B60b6Df7859A689715d092']
            }
        ]
    }

@pytest.mark.asyncio
async def test_create_multi_account_wallet_custom(key_manager):

    from pypergraph.keyring import account_registry

    account_registry.add_account("Custom", CustomAccount)

    wallet = MultiAccountWallet()
    wallet.create(network="Custom", label="New Custom", mnemonic=mnemo, num_of_accounts=3)
    assert wallet.get_state() == {
        'id': 'MAW5',
        'type': 'MAW',
        'label': 'New Custom',
        'supported_assets': ['ETH', 'ERC20'],
        'accounts': [
            {'address': 'FAKE_ADDRESS', 'supported_assets': ['FAKE1', 'FAKE2']},
            {'address': 'FAKE_ADDRESS', 'supported_assets': ['FAKE1', 'FAKE2']},
            {'address': 'FAKE_ADDRESS', 'supported_assets': ['FAKE1', 'FAKE2']}
        ]
    }