from dag_network import DEFAULT_L1_BASE_URL

import requests

from dag_keystore import KeyStore

from dag_network import API


def main():
    """Test stuff"""
    print("Step 1: Create new wallet")
    mnemonic_values = KeyStore.get_mnemonic()
    private_key = KeyStore.get_private_key_from_seed(seed=mnemonic_values["seed"])
    public_key = KeyStore.get_public_key_from_private_key(private_key.hex())
    dag_addr = KeyStore.get_dag_address_from_public_key(public_key=public_key.hex())
    KeyStore.get_p12_from_private_key(private_key)
    print("Done!")
    print("Step 2: Generate Transaction")
    amount = 1  # 1 DAG
    fee = 0.1  # Transaction fee
    from_address = dag_addr
    to_address = 'DAG4o8VYNg34Mnxp9mT4zDDCZTvrHWniscr3aAYv'
    last_ref = API.get_last_reference(dag_address=dag_addr)
    tx, tx_hash, encoded_tx = KeyStore.prepare_tx(amount, to_address, from_address, last_ref, fee)
    signature = KeyStore.sign(private_key_hex=private_key.hex(), tx_hash=tx_hash)
    proof = {"id": public_key.hex()[2:], "signature": signature}
    tx.add_proof(proof=proof)
    print(tx.get_post_transaction())
    print("Done!")
    print("Step 3: Post Transaction")
    resp = API.post_transaction(tx.get_post_transaction())

if __name__ == "__main__":
    main()



