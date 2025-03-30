import pytest

from pypergraph.keyring import KeyringManager, MultiKeyWallet, MultiAccountWallet
from pypergraph.keyring.accounts.dag_asset_library import dag_asset_library
from pypergraph.keyring.accounts.eth_asset_library import eth_asset_library
from pypergraph.keyring.models.kcs import KeyringAssetInfo
from pypergraph.keyring.tests.secret import mnemo, from_address
from pypergraph.keystore import KeyStore

# We need to write some more tests

@pytest.fixture
def key_manager():
    return KeyringManager(storage_file_path="key_storage.json")

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
    assert [wallet.id for wallet in key_manager.wallets] == ['SAW4', 'MCW5']

@pytest.mark.asyncio
async def test_manager_login(key_manager):
    """Retrieves data from encryted json storage"""
    await key_manager.login("super_S3cretP_Asswo0rd")
    print(key_manager.get_accounts())
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

@pytest.mark.asyncio
async def test_add_tokens(key_manager):
    """Retrieves data from encryted json storage"""
    # TODO: Check Stargazer to see how this is used.
    await key_manager.login("super_S3cretP_Asswo0rd")
    pytest.exit(key_manager.wallets)
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
    if not w_state == {'id': 'SAW1', 'type': 'SAW', 'label': 'New SAW', 'supported_assets': ['DAG'], 'accounts': [{'address': 'DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX', 'network': 'Constellation', 'tokens': []}]}:
        print(wallet.id)
        pytest.exit(key_manager.wallets)
    assert w_network == "Constellation"
    assert w_label == "New SAW"
    account = wallet.get_accounts()[0]
    account.set_tokens(dag_asset_library.imported_assets) # One would probably want to rely on different controllers for a wallet build
    assert account.get_state() == {'address': 'DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX', 'supported_assets': ['DAG'], 'tokens': {'PACA': KeyringAssetInfo(id='DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43', label='El Paca', symbol='PACA', decimals=8, native=None, network='mainnet', address='DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43'), 'DOR': KeyringAssetInfo(id='DAG0CyySf35ftDQDQBnd1bdQ9aPyUdacMghpnCuM', label='Dor', symbol='DOR', decimals=8, native=None, network='mainnet', address='DAG0CyySf35ftDQDQBnd1bdQ9aPyUdacMghpnCuM')}}




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
    assert wallet.model_dump() == {
        'type': 'MKW',
        'label': 'New MKW',
        'secret': None,
        'rings': [
            {
                'network': 'Constellation',
                'accounts': [
                    {
                        'private_key': '18e19114377f0b4ae5b9426105ffa4d18c791f738374b5867ebea836e5722710',
                        'label': 'Keyring 1'
                    }
                ]
            },
            {
                'network': 'Constellation',
                'accounts': [
                    {
                        'private_key': '18e19114377f0b4ae5b9426105ffa4d18c791f738374b5867ebea836e5722710',
                        'label': 'Keyring 2'
                    }
                ]
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_multi_account_wallet(key_manager):

    wallet = MultiAccountWallet()
    wallet.create(network="Constellation", label="New MAW", mnemonic=mnemo, num_of_accounts=2)
    model = wallet.model_dump()
    for i, account in enumerate(model["rings"][0][1]):
        model["rings"][0][1][i]["wallet"] = f"TEST_SIGNING_KEY_PLACEHOLDER_{i}"
    model["rings"][1] = ('hd_path', 'TEST_HD_PATH_PLACEHOLDER')
    model["rings"][4] = ('root_key', 'TEST_BIP32_KEY_PLACEHOLDER')
    assert model == {
        'type': 'MAW',
        'label': 'New MAW',
        'secret': 'multiply angle perfect verify behind sibling skirt attract first lift remove fortune',
        'rings': [
            (
                'accounts', [
                    {
                        'tokens': [],
                        'wallet': 'TEST_SIGNING_KEY_PLACEHOLDER_0',
                        'assets': [],
                        'bip44_index': 0,
                        'provider': None,
                        'label': None
                    },
                    {
                        'tokens': [],
                        'wallet': 'TEST_SIGNING_KEY_PLACEHOLDER_1',
                        'assets': [],
                        'bip44_index': 1,
                        'provider': None,
                        'label': None
                    }
                ]
            ),
            ('hd_path', 'TEST_HD_PATH_PLACEHOLDER'),
            ('mnemonic', 'multiply angle perfect verify behind sibling skirt attract first lift remove fortune'),
            ('extended_key', None),
            ('root_key', 'TEST_BIP32_KEY_PLACEHOLDER'),
            ('network', 'Constellation')
        ]
    }
    wallet.create(network="Ethereum", label="New MAW", mnemonic=mnemo, num_of_accounts=1)
    model = wallet.model_dump()
    vk = model["rings"][0][1][0]["wallet"].get_verifying_key().to_string()
    import eth_keys
    address = eth_keys.keys.PublicKey(vk).to_address()
    assert address == '0x8fbc948ba2dd081a51036de02582f5dcb51a310c'
