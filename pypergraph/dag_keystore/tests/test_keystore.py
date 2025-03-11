import hashlib

import eth_hash.auto
import eth_utils
import pytest
from docutils.nodes import address
from eth_account.hdaccount import ETHEREUM_DEFAULT_PATH
from eth_utils import keccak, to_checksum_address

from pypergraph.dag_core import BIP_44_PATHS
from pypergraph.dag_keystore import Bip32
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
async def test_encrypt_decrypt_keystore_v3():
    from eth_keys import keys
    print()
    keystore = KeyStore()
    phrase = "multiply angle perfect verify behind sibling skirt attract first lift remove fortune"
    keystore.validate_mnemonic(phrase)
    pk = keystore.get_private_key_from_mnemonic(phrase)
    enc_data = keystore.encrypt_keystore_from_private_key(private_key=pk, password="top_secret")
    dec_pk = keystore.decrypt_keystore_private_key(data=enc_data, password='top_secret')
    assert dec_pk == pk
    await keystore.write_keystore_file('keystore.json', enc_data)
    enc_data = await keystore.load_keystore_file('keystore.json')
    dec_pk = keystore.decrypt_keystore_private_key(data=enc_data, password='top_secret')
    assert dec_pk == pk
    # Convert private key to bytes
    eth_path = BIP_44_PATHS.ETH_WALLET_PATH.value+'/0'
    cn_path = BIP_44_PATHS.CONSTELLATION_PATH.value+'/0'
    from pypergraph.dag_keystore import mnemonic_utils
    eth_private_key = mnemonic_utils.mnemonic_to_private_key(phrase, str_derivation_path=eth_path)
    cn_private_key = mnemonic_utils.mnemonic_to_private_key(phrase, str_derivation_path=cn_path)
    eth_public_key = keys.PrivateKey(eth_private_key).public_key
    cn_public_key = keys.PrivateKey(cn_private_key).public_key
    eth_address = eth_public_key.to_address()
    cn_address = keystore.get_dag_address_from_public_key(cn_public_key.to_hex()[2:])
    print(eth_address, cn_address)


""" I would like to make it mor clear that 'encryptor' is custom, and that the above methods are industry standards"""
