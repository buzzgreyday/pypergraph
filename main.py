from dag_keystore import KeyStore

from dag_network import API
from dag_wallet import Wallet


def main():
    """Test stuff"""
    print("Step 1: Create new wallet")
    wallet = Wallet.new()
    wallet = Wallet(address=wallet.address, public_key=wallet.public_key, private_key=wallet.private_key, words=wallet.words)
    print("Done!")
    print("Step 2: Generate Transaction")
    amount = 1  # 1 DAG
    fee = 0.1  # Transaction fee
    from_address = wallet.address
    to_address = 'DAG4o8VYNg34Mnxp9mT4zDDCZTvrHWniscr3aAYv'
    last_ref = API.get_last_reference(dag_address=wallet.address)
    tx, tx_hash, encoded_tx = KeyStore.prepare_tx(amount, to_address, from_address, last_ref, fee)
    signature = KeyStore.sign(private_key_hex=wallet.private_key, tx_hash=tx_hash)
    proof = {"id": wallet.public_key[2:], "signature": signature}
    tx.add_proof(proof=proof)
    print(tx.get_post_transaction())
    print("Done!")
    print("Step 3: Post Transaction")
    resp = API.post_transaction(tx.get_post_transaction())

if __name__ == "__main__":
    main()



