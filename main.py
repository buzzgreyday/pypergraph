import requests
from pydantic import BaseModel

from dag_keystore import Bip32, Bip39, Wallet

# dag4.dag-network.src.dto.v2.transactions.ts

class TransactionReference(BaseModel):
    hash: str
    ordinal: int

class TransactionValueV2(BaseModel):
    source: str
    destination: str
    amount: float
    fee: float
    parent: TransactionReference
    salt: int | str

class TransactionV2(BaseModel):
    hash: str
    source: str
    destination: str
    amount: float
    fee: float
    parent: TransactionReference
    snapshot: str
    block: str
    timestamp: str
    transactionOriginal: TransactionReference

class Proof(BaseModel):
    signature: str
    id: str

class PostTransactionV2(BaseModel):
    value: TransactionValueV2
    proofs: Proof

class PostTransactionResponseV2(BaseModel):
    hash: str

class GetTransactionResponseV2(BaseModel):
    data: TransactionV2

# dag4.dag-network.src.DNC.ts
class DNC:
    BLOCK_EXPLORER_URL = 'https://block-explorer.constellationnetwork.io'
    LOAD_BALANCER_URL = 'http://lb.constellationnetwork.io:9000'
    L0_URL = 'http://13.52.246.74:9000'
    L1_URL = 'http://13.52.246.74:9010'

class RestApi:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx or 5xx
        return response.json()


class L1Api:
    def __init__(self, base_urls):
        """
        Initialize with a dictionary of base URLs, where each key is a label for the URL.
        Example: {"main": "https://main-api.com", "backup": "https://backup-api.com"}
        """
        self.services = {key: RestApi(url) for key, url in base_urls.items()}
        self.current_service_key = next(iter(base_urls))  # Default to the first URL

    def set_service(self, key):
        """
        Switch to a different base URL by its key.
        """
        if key not in self.services:
            raise ValueError(f"Invalid service key: {key}")
        self.current_service_key = key

    # dag4.dag-network.src.api.v2.l1-api.ts
    def get_address_last_accepted_transaction_ref(self, address) -> TransactionReference:
        """
        Fetch the transaction reference and parse it into a TransactionReference object.
        """
        endpoint = f"/transactions/last-reference/{address}"
        response_data = self.services[self.current_service_key].get(endpoint)
        return TransactionReference(**response_data)  # Parse the response into a TransactionReference

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

if __name__ == "__main__":
    main()



