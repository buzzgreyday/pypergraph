from dag_keystore import Bip32, Bip39
from dag_network import DEFAULT_L1_BASE_URL
from dag_wallet import Wallet

import requests

from dag_keystore import KeyStore

class API:
    @staticmethod
    def get_last_reference(dag_address: str):

        endpoint = f"/transactions/last-reference/{dag_address}"
        url = DEFAULT_L1_BASE_URL + endpoint
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

def main():
    """Test stuff"""
    print("Step 1: Create new wallet")
    mnemonic_values = KeyStore.get_mnemonic()
    private_key = KeyStore.get_private_key_from_seed(seed=mnemonic_values["seed"])
    public_key = KeyStore.get_public_key_from_private_key(private_key.hex())
    dag_addr = KeyStore.get_dag_address_from_public_key(public_key=public_key.hex())
    KeyStore.get_p12_from_private_key(private_key)
    print("Done!")

    print("Step 2: Get Last Reference")
    last_ref = API.get_last_reference(dag_address=dag_addr)
    print("Done!")

    print("Step 3: Generate Transaction.")

    amount = 1  # 1 DAG
    fee = 0.1  # Transaction fee
    from_address = dag_addr
    to_address = 'DAG4o8VYNg34Mnxp9mT4zDDCZTvrHWniscr3aAYv'
    last_ref = last_ref

    d = KeyStore.prepare_tx(amount, to_address, from_address, last_ref, fee)
    tx = d["tx"]
    tx_hash = d["hash"]

    signature = KeyStore.sign(private_key_hex=private_key.hex(), tx_hash=tx_hash)
    tx["proofs"].append({"id": public_key.hex()[2:], "signature": signature})
    print("Tx to Post:", tx)
    print()

    print("Step 3: Post Transaction")
    # Define the URL and headers
    url = "https://l1-lb-mainnet.constellationnetwork.io/transactions"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=tx)

    # Print the response
    print("Status Code:", response.status_code)
    print("Response Body:", response.json())
    # api.post_transaction(tx)

if __name__ == "__main__":
    main()



