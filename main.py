import requests

from dag_keystore import Bip32, Bip39, Wallet
from dag_network.api import Api

BASE_URLS = {
                "BLOCK_EXPLORER_URL": 'https://block-explorer.constellationnetwork.io',
                "LOAD_BALANCER_URL": 'http://lb.constellationnetwork.io:9000',
                "L0_URL": 'https://l0-lb-mainnet.constellationnetwork.io',
                "L1_URL": 'https://l1-lb-mainnet.constellationnetwork.io',
            }

# packages/dag4-core/src/cross-platform/api/rest.api.ts




def main():
    """Create wallet and test: This is done"""
    bip39 = Bip39()
    bip32 = Bip32()
    wallet = Wallet()
    mnemonic_values = bip39.mnemonic()
    private_key = bip32.get_private_key_from_seed(seed_bytes=mnemonic_values["seed"])
    public_key = bip32.get_public_key_from_private_hex(private_key_hex=private_key)
    dag_addr = wallet.get_dag_address_from_public_key_hex(public_key_hex=public_key)
    print("Values:", mnemonic_values, "\nPrivate Key: " + private_key, "\nPublic Key: " + public_key, "\nDAG Address: " + dag_addr)
    derived_seed = bip39.get_seed_from_mnemonic(words=mnemonic_values["words"])
    derived_private_key = bip32.get_private_key_from_seed(seed_bytes=derived_seed)
    derived_public_key = bip32.get_public_key_from_private_hex(private_key_hex=derived_private_key)
    derived_dag_addr = wallet.get_dag_address_from_public_key_hex(public_key_hex=derived_public_key)
    print(derived_dag_addr, derived_private_key, derived_public_key, derived_seed)

    """Get last reference"""
    try:
        api = Api(BASE_URLS["L1_URL"])  # Pass a single URL instead of the whole dictionary
        transaction_ref = api.get_address_last_accepted_transaction_ref(derived_dag_addr)
        print(transaction_ref)
    except requests.HTTPError as e:
        print(f"HTTP error occurred with main service: {e}")
    except ValueError as ve:
        print(f"Validation error occurred: {ve}")

if __name__ == "__main__":
    main()



