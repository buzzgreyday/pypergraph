import pytest

from pypergraph.dag_core import BIP_44_PATHS
from pypergraph.dag_keystore.keystore import KeyStore

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
    mnemo = keystore.get_mnemonic()
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
    cn_private_key = keystore.get_private_key_from_mnemonic(phrase="multiply angle perfect verify behind sibling skirt attract first lift remove fortune", path=BIP_44_PATHS.CONSTELLATION_PATH.value)
    eth_private_key = keystore.get_private_key_from_mnemonic(phrase="multiply angle perfect verify behind sibling skirt attract first lift remove fortune", path=BIP_44_PATHS.ETH_WALLET_PATH.value)
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
    print(await keystore.generate_encrypted_private_key(eth_private_key))
