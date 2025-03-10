import pytest

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


def test_encrypt_decrypt_keystore_v3():
    keystore = KeyStore()
    phrase = "multiply angle perfect verify behind sibling skirt attract first lift remove fortune"
    keystore.validate_mnemonic(phrase)
    pk = keystore.get_private_key_from_mnemonic(phrase)
    enc_data = keystore.encrypt_keystore_from_private_key(private_key=pk, password="top_secret")
    dec_pk = keystore.decrypt_keystore_private_key(data=enc_data, password='top_secret')
    assert dec_pk == pk
    keystore.write_keystore_file('', enc_data)
    enc_data = keystore.load_keystore_file('', 'top_secret')
    dec_pk = keystore.decrypt_keystore_private_key(data=enc_data, password='top_secret')
    assert dec_pk == pk

""" I would like to make it mor clear that 'encryptor' is custom, and that the above methods are industry standards"""
