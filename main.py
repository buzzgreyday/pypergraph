# Generate transaction
from decimal import Decimal, ROUND_DOWN
from typing import Optional
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_der_private_key
from cryptography.hazmat.backends import default_backend

import requests

from dag_keystore import Bip32, Bip39, Wallet
from dag_network import NetworkApi, PostTransactionV2, TransactionReference, Proof
from dag_network import DEFAULT_L1_BASE_URL

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

class TransactionGenerator:
    def __init__(self, key_store, use_fallback_lib=False):
        self.use_fallback_lib = use_fallback_lib
        self.key_store = key_store

    async def generate_transaction_with_hash_v2(
            self,
            amount: float,
            to_address: str,
            key_trio: dict,
            last_ref: dict,
            fee: float = 0
    ):
        from_address = key_trio.get("address")
        public_key = key_trio.get("public_key")
        private_key = key_trio.get("private_key")

        if not private_key:
            raise ValueError("No private key set")

        if not public_key:
            raise ValueError("No public key set")

        # Prepare the transaction and hash
        tx, hash_ = self.prepare_tx(amount, to_address, from_address, last_ref, fee, "2.0")

        # Sign the transaction hash
        signature = await self.sign(private_key, hash_)

        # Handle uncompressed public key
        uncompressed_public_key = (
            "04" + public_key if len(public_key) == 128 else public_key
        )

        # Verify the signature
        if not self.verify(uncompressed_public_key, hash_, signature):
            raise ValueError("Sign-Verify failed")

        # Construct the signature element
        # signature_elt = {
        #     "id": uncompressed_public_key[2:],  # Remove the "04" prefix
        #     "signature": signature,
        # }

        # Assuming `tx_encode.get_v2_tx_from_post_transaction(tx)` returns a dictionary compatible with PostTransactionV2
        #transaction_data = tx_encode.get_v2_tx_from_post_transaction(tx)

        # Create a transaction object using the PostTransactionV2 model
        transaction = PostTransactionV2(**tx)

        # Create a Proof object for the signature
        signature_elt = Proof(id=uncompressed_public_key[2:], signature=signature)

        # Add the Proof to the transaction's proofs list by creating a new instance
        updated_transaction = transaction.copy(
            update={"proofs": transaction.proofs + [signature_elt]}
        )

        # `updated_transaction` now contains the added signature
        print(updated_transaction)

        return {
            "hash": hash_,
            "transaction": transaction.get_post_transaction(),
        }

    def prepare_tx(
        self,
        amount: float,
        to_address: str,
        from_address: str,
        last_ref: dict,
        fee: float = 0,
        version: str = "2.0",
    ) -> dict:
        if to_address == from_address:
            raise ValueError("An address cannot send a transaction to itself")

        # Normalize to integer and preserve 8 decimals of precision
        amount = self._normalize_amount(amount)
        fee = self._normalize_amount(fee)

        if amount < 1:
            raise ValueError("Send amount must be greater than 1e-8")

        if fee < 0:
            raise ValueError("Send fee must be greater or equal to zero")

        tx = self.tx_encode.get_tx_v2(amount, to_address, from_address, last_ref, fee)
        encoded_tx = tx.get_encoded()

        # Serialize the transaction
        serialized_tx = self.tx_encode.kryo_serialize(encoded_tx, version == "1.0")

        # Calculate the hash
        hash_ = self._sha256(bytes.fromhex(serialized_tx))

        # Return the prepared transaction data
        return {
            "tx": tx.get_post_transaction(),
            "hash": hash_,
            "rle": encoded_tx,
        }

    @staticmethod
    def _normalize_amount(value: float) -> int:
        # Normalize to an integer with 8 decimal places
        return int(Decimal(value).scaleb(8).quantize(Decimal("1"), rounding=ROUND_DOWN))

    async def sign(self, private_key: str, msg: str) -> str:
        sha512_hash = self.sha512(msg)

        if self.use_fallback_lib:
            # Use the fallback library for signing
            ec_private_key = ec.derive_private_key(
                int(private_key, 16), ec.SECP256K1(), default_backend()
            )
            signature = ec_private_key.sign(
                sha512_hash, ec.ECDSA(hashes.SHA512())
            )
            return signature.hex()

        # Use secp library for signing
        from coincurve import PrivateKey
        priv_key = PrivateKey(bytes.fromhex(private_key))
        signature = priv_key.sign(sha512_hash, hasher=None)
        return signature.hex()

    @staticmethod
    def sha512(message: str) -> bytes:
        return hashlib.sha512(message.encode('utf-8')).digest()

    @staticmethod
    def _sha256(data: bytes) -> str:
        # Compute SHA-256 hash
        return hashlib.sha256(data).hexdigest()

    def verify(self, public_key: str, msg: str, signature: str) -> bool:
        sha512_hash = self.sha512(msg)

        if self.use_fallback_lib:
            # Use fallback library for verification
            ec_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256K1(), bytes.fromhex(public_key)
            )
            try:
                ec_public_key.verify(
                    bytes.fromhex(signature),
                    sha512_hash,
                    ec.ECDSA(hashes.SHA512())
                )
                return True
            except Exception:
                return False

        # Use coincurve for verification
        from coincurve import PublicKey
        pub_key = PublicKey(bytes.fromhex(public_key))
        return pub_key.verify(bytes.fromhex(signature), sha512_hash, hasher=None)

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



if __name__ == "__main__":
    main()



