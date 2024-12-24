# Generate transaction
import array
import struct
from decimal import Decimal, ROUND_DOWN
import random
from typing import Optional, Dict, Any
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


MIN_SALT = 1  # Replace with the actual minimum salt value

class TransactionV2:
    def __init__(self, from_address=None, to_address=None, amount=None, fee=0, last_tx_ref=None, salt=None):
        self.tx = {
            "value": {
                "source": from_address,
                "destination": to_address,
                "amount": amount,
                "fee": fee,
                "parent": last_tx_ref,
                "salt": salt or MIN_SALT + random.randint(0, 2**48 - 1)
            },
            "proofs": []
        }

    @staticmethod
    def from_post_transaction(tx):
        return TransactionV2(
            from_address=tx["value"]["source"],
            to_address=tx["value"]["destination"],
            amount=tx["value"]["amount"],
            fee=tx["value"]["fee"],
            last_tx_ref=tx["value"]["parent"],
            salt=tx["value"]["salt"]
        )

    @staticmethod
    def to_hex_string(value):
        value = Decimal(value)
        if value < 0:
            value += 1 << 64  # Handle negative values with two's complement
        return hex(int(value))[2:]  # Convert to hex and strip "0x"

    def get_post_transaction(self):
        return {
            "value": {
                **self.tx["value"],
                "salt": str(self.tx["value"]["salt"]).replace("n", "")
            },
            "proofs": list(self.tx["proofs"])
        }

    def get_encoded(self):
        parent_count = "2"  # Always 2 parents
        source_address = self.tx["value"]["source"]
        dest_address = self.tx["value"]["destination"]
        amount = self.to_hex_string(self.tx["value"]["amount"])
        parent_hash = self.tx["value"]["parent"]["hash"]
        ordinal = str(self.tx["value"]["parent"]["ordinal"])
        fee = str(self.tx["value"]["fee"])
        salt = self.to_hex_string(self.tx["value"]["salt"])

        return "".join([
            parent_count,
            str(len(source_address)),
            source_address,
            str(len(dest_address)),
            dest_address,
            str(len(amount)),
            amount,
            str(len(parent_hash)),
            parent_hash,
            str(len(ordinal)),
            ordinal,
            str(len(fee)),
            fee,
            str(len(salt)),
            salt
        ])

    def set_encoded_hash_reference(self):
        # NOOP
        pass

    def set_signature_batch_hash(self, hash_value):
        # NOOP
        pass

    def add_signature(self, proof):
        self.tx["proofs"].append(proof)

class KryoSerializer:
    @staticmethod
    def utf8_length(value: int) -> bytes:
        """
        Encodes the given value into a custom UTF-8-like format.

        :param value: The integer value to encode.
        :return: A bytes object representing the encoded value.
        """
        if value < 0:
            raise ValueError("Value must be non-negative.")

        buffer = array.array('B')  # Create a buffer for byte values

        if value >> 6 == 0:
            # 1-byte encoding
            buffer.append(value | 0x80)  # Set bit 8
        elif value >> 13 == 0:
            # 2-byte encoding
            buffer.append((value & 0x3F) | 0x40 | 0x80)  # Set bits 7 and 8
            buffer.append(value >> 6)
        elif value >> 20 == 0:
            # 3-byte encoding
            buffer.append((value & 0x3F) | 0x40 | 0x80)  # Set bits 7 and 8
            buffer.append(((value >> 6) & 0x7F) | 0x80)  # Set bit 8
            buffer.append(value >> 13)
        elif value >> 27 == 0:
            # 4-byte encoding
            buffer.append((value & 0x3F) | 0x40 | 0x80)  # Set bits 7 and 8
            buffer.append(((value >> 6) & 0x7F) | 0x80)  # Set bit 8
            buffer.append(((value >> 13) & 0x7F) | 0x80)  # Set bit 8
            buffer.append(value >> 20)
        else:
            # 5-byte encoding
            buffer.append((value & 0x3F) | 0x40 | 0x80)  # Set bits 7 and 8
            buffer.append(((value >> 6) & 0x7F) | 0x80)  # Set bit 8
            buffer.append(((value >> 13) & 0x7F) | 0x80)  # Set bit 8
            buffer.append(((value >> 20) & 0x7F) | 0x80)  # Set bit 8
            buffer.append(value >> 27)

        return buffer.tobytes()

    def kryo_serialize(self, msg: str, set_references: bool = True) -> str:
        """
        Serializes a message with a prefix for Kryo serialization.

        :param msg: The message to serialize.
        :param set_references: Whether to include the reference flag in the prefix.
        :return: The serialized string in hex format.
        """
        prefix = "03" + ("01" if set_references else "") + self.utf8_length(len(msg) + 1).hex()
        coded = msg.encode("utf-8").hex()

        return prefix + coded

class TransactionGenerator:
    def __init__(self, use_fallback_lib=False):
        self.use_fallback_lib = use_fallback_lib

    def generate_transaction_with_hash_v2(
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
        tx, hash_ = self.prepare_tx(amount, to_address, from_address, last_ref, fee)

        # Sign the transaction hash
        signature = self.sign(private_key, hash_)

        # Handle uncompressed public key
        uncompressed_public_key = (
            "04" + public_key if len(public_key) == 128 else public_key
        )

        # Verify the signature
        if not self.verify(uncompressed_public_key, hash_, signature):
            raise ValueError("Sign-Verify failed")

        # Construct the signature element
        signature_elt = {
            "id": uncompressed_public_key[2:],  # Remove the "04" prefix
            "signature": signature,
        }


        # Assuming `tx_encode.get_v2_tx_from_post_transaction(tx)` returns a dictionary compatible with PostTransactionV2
        #transaction_data = tx_encode.get_v2_tx_from_post_transaction(tx)

        # Create a transaction object using the PostTransactionV2 model
        #transaction = PostTransactionV2(**tx)

        # Create a Proof object for the signature
        #signature_elt = Proof(id=uncompressed_public_key[2:], signature=signature)

        # Add the Proof to the transaction's proofs list by creating a new instance
        #updated_transaction = transaction.copy(
        #    update={"proofs": transaction.proofs + [signature_elt]}
        #)

        # `updated_transaction` now contains the added signature
        #print(updated_transaction)
        tx.add_signature(proof=signature_elt)
        print(tx.__dict__)

        return {
            "hash": hash_,
            "transaction": tx.get_post_transaction(),
        }

    def prepare_tx(
        self,
        amount: float,
        to_address: str,
        from_address: str,
        last_ref: dict,
        fee: float = 0,
    ) -> tuple:
        if to_address == from_address:
            raise ValueError("An address cannot send a transaction to itself")

        # Normalize to integer and preserve 8 decimals of precision
        amount = self._normalize_amount(amount)
        fee = self._normalize_amount(fee)

        if amount < 1:
            raise ValueError("Send amount must be greater than 1e-8")

        if fee < 0:
            raise ValueError("Send fee must be greater or equal to zero")

        tx = TransactionV2(amount=amount, to_address=to_address, from_address=from_address, last_tx_ref=last_ref, fee=fee)
        encoded_tx = tx.get_encoded()

        # Serialize the transaction
        serialized_tx = KryoSerializer().kryo_serialize(encoded_tx)

        # Calculate the hash
        hash_ = self._sha256(bytes.fromhex(serialized_tx))

        # Return the prepared transaction data
        return tx, hash_
        #return {
        #    "tx": tx.get_post_transaction(),
        #    "hash": hash_,
        #    "rle": encoded_tx,
        #}

    @staticmethod
    def _normalize_amount(value: float) -> int:
        # Normalize to an integer with 8 decimal places
        return int(Decimal(value).scaleb(8).quantize(Decimal("1"), rounding=ROUND_DOWN))

    def sign(self, private_key: str, msg: str) -> str:
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
    print("pypergraph wallet (early alpha)")
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
    key_trio = {"address": dag_addr, "public_key": public_key, "private_key": private_key}
    transaction_generator = TransactionGenerator(use_fallback_lib=True)
    transaction_generator.generate_transaction_with_hash_v2(amount=1, to_address="DAG4CKOFF", key_trio=key_trio, last_ref=transaction_ref, fee=0)

    """Post Transaction"""


if __name__ == "__main__":
    main()



