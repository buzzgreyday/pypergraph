import json

import pytest

from pypergraph import DagTokenNetwork
from pypergraph.core import BIP_44_PATHS
from pypergraph.keystore.keystore import KeyStore

def test_get_keys_from_mnemonic():
    keystore = KeyStore()
    phrase = "multiply angle perfect verify behind sibling skirt attract first lift remove fortune"
    keystore.validate_mnemonic(phrase)
    pk = keystore.get_private_key_from_mnemonic(phrase)
    pubk = keystore.get_public_key_from_private(pk)
    address = keystore.get_dag_address_from_public_key(pubk)
    keystore.validate_address(address)
    assert pk == '18e19114377f0b4ae5b9426105ffa4d18c791f738374b5867ebea836e5722710'
    assert pubk == '044462191fb1056699c28607c7e8e03b73602fa070b78cad863b5f84d08a577d5d0399ccd90ba1e69f34382d678216d4b2a030d98e38c0c960447dc49514f92ad7'
    assert address == 'DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX'


def test_new_keys():
    keystore = KeyStore()
    mnemo = keystore.generate_mnemonic()
    keystore.validate_mnemonic(mnemo)
    pk = keystore.get_private_key_from_mnemonic(mnemo)
    pubk = keystore.get_public_key_from_private(pk)
    address = keystore.get_dag_address_from_public_key(pubk)
    keystore.validate_address(address)
    pk = keystore.generate_private_key()
    pubk = keystore.get_public_key_from_private(pk)
    address = keystore.get_dag_address_from_public_key(pubk)
    keystore.validate_address(address)

@pytest.mark.asyncio
async def test_create_keystores():
    keystore = KeyStore()
    cn_private_key = keystore.get_private_key_from_mnemonic(
        phrase="multiply angle perfect verify behind sibling skirt attract first lift remove fortune",
        derivation_path=BIP_44_PATHS.CONSTELLATION_PATH.value
    )
    eth_private_key = keystore.get_private_key_from_mnemonic(
        phrase="multiply angle perfect verify behind sibling skirt attract first lift remove fortune",
        derivation_path=BIP_44_PATHS.ETH_WALLET_PATH.value
    )
    assert eth_private_key == '7bdf99e47c15ea9ce32b2306f1cf2d88be5f541e5a90fe92dedb795ea2a53e19'
    assert cn_private_key == '18e19114377f0b4ae5b9426105ffa4d18c791f738374b5867ebea836e5722710'
    cn_public_key = keystore.get_public_key_from_private(private_key=cn_private_key)
    eth_public_key = keystore.get_public_key_from_private(private_key=eth_private_key)[2:]
    assert '0x'+eth_public_key == '0x65879c90895c191fe27bc9fee6b6a6a8d49b41600429e151687b0a274c2174f8c263a55008a3009cd5230fb526141558ee1aace50d54cc24b91fa4e19b79e5a7'
    assert cn_public_key == '044462191fb1056699c28607c7e8e03b73602fa070b78cad863b5f84d08a577d5d0399ccd90ba1e69f34382d678216d4b2a030d98e38c0c960447dc49514f92ad7'
    cn_address = keystore.get_dag_address_from_public_key(cn_public_key)
    eth_address = keystore.get_eth_address_from_public_key(eth_public_key)
    assert eth_address == '0x8fbc948ba2dd081a51036de02582f5dcb51a310c'
    assert cn_address == 'DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX'
    encrypted_private_key = keystore.generate_encrypted_private_key(private_key=eth_private_key, password='top_secret')
    decrypted_private_key = keystore.decrypt_private_key(encrypted_private_key, 'top_secret')
    assert decrypted_private_key == '7bdf99e47c15ea9ce32b2306f1cf2d88be5f541e5a90fe92dedb795ea2a53e19'
    assert isinstance(json.dumps(encrypted_private_key), str)
    encrypted_phrase = await keystore.encrypt_phrase(
        phrase="multiply angle perfect verify behind sibling skirt attract first lift remove fortune",
        password='top_secret'
    )
    decrypted_phrase = await keystore.decrypt_phrase(encrypted_phrase, password='top_secret')
    assert decrypted_phrase == "multiply angle perfect verify behind sibling skirt attract first lift remove fortune"


def test_get_accounts_from_master_key():
    keystore = KeyStore()
    master_key = keystore.get_master_key_from_mnemonic(
        "multiply angle perfect verify behind sibling skirt attract first lift remove fortune",
        derivation_path=BIP_44_PATHS.ETH_WALLET_PATH.value)
    eth_private_key = keystore.derive_account_from_master_key(master_key, index=0)
    eth_private_key_index_1 = keystore.derive_account_from_master_key(master_key, index=1)
    assert eth_private_key == '7bdf99e47c15ea9ce32b2306f1cf2d88be5f541e5a90fe92dedb795ea2a53e19'
    assert eth_private_key_index_1 == 'edb3dd50d1169cc62bf1e35ccf6ef596b3d99ebdf74ab365cdb4888e655dcb21'
    master_key = keystore.get_master_key_from_mnemonic(
        "multiply angle perfect verify behind sibling skirt attract first lift remove fortune"
    )
    cn_private_key = keystore.derive_account_from_master_key(master_key, index=0)
    cn_private_key_index_1 = keystore.derive_account_from_master_key(master_key, index=1)
    assert cn_private_key == '18e19114377f0b4ae5b9426105ffa4d18c791f738374b5867ebea836e5722710'
    assert cn_private_key_index_1 == 'edaa15ec384bced99e66960d3f0c6be25b00c0322f065c33418459f2228f6724'

def test_get_addresses_from_private_key():
    keystore = KeyStore()
    eth_private_key = keystore.get_private_key_from_mnemonic(
        "multiply angle perfect verify behind sibling skirt attract first lift remove fortune",
        derivation_path=BIP_44_PATHS.ETH_WALLET_PATH.value)
    eth_address = keystore.get_eth_address_from_private_key(eth_private_key)
    assert eth_address == '0x8fbc948ba2dd081a51036de02582f5dcb51a310c'

@pytest.mark.asyncio
async def test_generate_transaction_and_verify_signature():
    keystore = KeyStore()
    phrase = "multiply angle perfect verify behind sibling skirt attract first lift remove fortune"
    keystore.validate_mnemonic(phrase)
    pk = keystore.get_private_key_from_mnemonic(phrase)
    pubk = keystore.get_public_key_from_private(pk)
    address = keystore.get_dag_address_from_public_key(pubk)
    last_ref = await DagTokenNetwork().get_address_last_accepted_transaction_ref(address)
    tx, hash_ = KeyStore.prepare_tx(
        amount=1000000,
        to_address="DAG5WLxvp7hQgumY7qEFqWZ9yuRghSNzLddLbxDN",
        from_address=address,
        last_ref=last_ref,
        fee=2000000,
    )
    signature = keystore.sign(pk, hash_)
    assert keystore.verify(pubk, hash_, signature)

def test_generate_custom_data_transaction_and_verify_signature():
    # Required imports
    import time
    import json
    import base64

    from pypergraph import KeyStore

    phrase = "multiply angle perfect verify behind sibling skirt attract first lift remove fortune"
    KeyStore.validate_mnemonic(phrase)
    pk = KeyStore.get_private_key_from_mnemonic(phrase)
    pubk = KeyStore.get_public_key_from_private(pk)
    address = KeyStore.get_dag_address_from_public_key(pubk)

    # Sample data to sign
    water_and_energy_usage = {
        "address": address,
        "energyUsage": {
            "usage": 7,
            "timestamp": int(time.time() * 1000),
        },
        "waterUsage": {
            "usage": 7,
            "timestamp": int(time.time() * 1000),
        },
    }

    # Custom encoding function example
    def encode(data: dict) -> str:
        return json.dumps(data, separators=(',', ':'))

    # Generate a signature and hash for the custom data
    signature, hash_value = KeyStore().data_sign(
        private_key=pk,
        msg=water_and_energy_usage,
        prefix=False,
        encoding=encode
    )

    encoded_msg = encode(water_and_energy_usage)
    assert KeyStore().verify_data(pubk, encoded_msg, signature)
