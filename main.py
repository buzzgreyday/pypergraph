from dag_wallet import Bip32, Bip39, Wallet

def main():
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
if __name__ == "__main__":
    main()



