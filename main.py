from typing import Optional

import requests

from dag_keystore import Bip32, Bip39, Wallet
from dag_network import NetworkApi, PostTransactionV2, TransactionReference
from dag_network import DEFAULT_L1_BASE_URL

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
    print("Success!" if derived_dag_addr == dag_addr else "Test failed")

    """Get last reference"""
    try:
        api = NetworkApi(DEFAULT_L1_BASE_URL)  # Pass a single URL instead of the whole dictionary
        transaction_ref = api.get_address_last_accepted_transaction_ref(derived_dag_addr)
        print(transaction_ref)
    except requests.HTTPError as e:
        print(f"HTTP error occurred with main service: {e}")
    except ValueError as ve:
        print(f"Validation error occurred: {ve}")

    """Generate signed transaction"""
    # packages/dag4-wallet/src/dag-account.ts
    class TransactionManager:
        def __init__(self, network, key_store, address, key_trio):
            self.network = network
            self.key_store = key_store
            self.address = address
            self.key_trio = key_trio

        async def generate_signed_transaction(
                self,
                to_address: str,
                amount: float,
                fee: float = 0,
                last_ref: Optional[TransactionReference] = None
        ) -> "PostTransactionV2":
            if last_ref is None:
                last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)

            return self.key_store.generate_transaction_v2(
                amount=amount,
                to_address=to_address,
                key_trio=self.key_trio,
                last_ref=last_ref,
                fee=fee,
            )


if __name__ == "__main__":
    main()



