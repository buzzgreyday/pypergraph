import binascii
import hashlib
from decimal import Decimal, ROUND_DOWN

import subprocess
import sys
import os

import secp256k1
from coincurve import PrivateKey, PublicKey

from dag_keystore import Bip32, Bip39, Wallet
from dag_network import DEFAULT_L1_BASE_URL

import requests

# prepareTx
import random
from decimal import Decimal
from dataclasses import dataclass, field

@dataclass
class PostTransactionV2:
    value: dict = field(default_factory=lambda: {
        "source": None,
        "destination": None,
        "amount": None,
        "fee": 0,
        "parent": None,
        "salt": None,
    })
    proofs: list = field(default_factory=list)


class TransactionV2:
    MIN_SALT = Decimal("1e8")

    def __init__(self, from_address=None, to_address=None, amount=None, fee=None, last_tx_ref=None, salt=None):
        self.tx = PostTransactionV2()

        if from_address:
            self.tx.value["source"] = from_address
        if to_address:
            self.tx.value["destination"] = to_address
        if amount is not None:
            self.tx.value["amount"] = amount
        if fee is not None:
            self.tx.value["fee"] = fee
        if last_tx_ref:
            self.tx.value["parent"] = last_tx_ref
        if salt is None:
            salt = self.MIN_SALT + int(random.getrandbits(48))
        self.tx.value["salt"] = salt

    @classmethod
    def from_post_transaction(cls, tx):
        return cls(
            amount=tx["value"]["amount"],
            from_address=tx["value"]["source"],
            to_address=tx["value"]["destination"],
            last_tx_ref=tx["value"]["parent"],
            salt=tx["value"]["salt"],
            fee=tx["value"]["fee"],
        )

    @staticmethod
    def to_hex_string(val):
        val = Decimal(val)
        if val < 0:
            b_int = (1 << 64) + int(val)
        else:
            b_int = int(val)
        return format(b_int, "x")

    def get_post_transaction(self):
        return {
            "value": {
                **self.tx.value,
                "salt": str(self.tx.value["salt"]).replace("n", ""),
            },
            "proofs": self.tx.proofs.copy(),
        }

    def get_encoded(self):
        parent_count = "2"  # Always 2 parents
        source_address = self.tx.value["source"]
        dest_address = self.tx.value["destination"]
        amount = format(self.tx.value["amount"], "x")  # amount as hex
        parent_hash = self.tx.value["parent"]["hash"]
        ordinal = str(self.tx.value["parent"]["ordinal"])
        fee = str(self.tx.value["fee"])
        salt = self.to_hex_string(self.tx.value["salt"])

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
            salt,
        ])

    def add_signature(self, proof):
        self.tx.proofs.append(proof)


class TxEncode:
    @staticmethod
    def get_tx_v2(amount, to_address, from_address, last_ref, fee=None):
        return TransactionV2(
            amount=amount,
            to_address=to_address,
            from_address=from_address,
            last_tx_ref=last_ref,
            fee=fee,
        )

    def kryo_serialize(self, msg: str, set_references: bool = True) -> str:
        """
        Serialize a message using a custom kryo-like serialization method.

        :param msg: The string message to serialize.
        :param set_references: Whether to include references in the prefix.
        :return: The serialized message as a hexadecimal string.
        """
        prefix = "03" + ("01" if set_references else "") + self.utf8_length(len(msg) + 1).hex()
        coded = msg.encode("utf-8").hex()
        return prefix + coded

    def utf8_length(self, value: int) -> bytes:
        """
        Encodes the length of a UTF8 string as a variable-length encoded integer.

        :param value: The value to encode.
        :return: The encoded length as a bytes object.
        """
        buffer = bytearray()

        if value >> 6 == 0:
            # Requires 1 byte
            buffer.append(value | 0x80)  # Set bit 8.
        elif value >> 13 == 0:
            # Requires 2 bytes
            buffer.append(value | 0x40 | 0x80)  # Set bits 7 and 8.
            buffer.append(value >> 6)
        elif value >> 20 == 0:
            # Requires 3 bytes
            buffer.append(value | 0x40 | 0x80)  # Set bits 7 and 8.
            buffer.append((value >> 6) | 0x80)  # Set bit 8.
            buffer.append(value >> 13)
        elif value >> 27 == 0:
            # Requires 4 bytes
            buffer.append(value | 0x40 | 0x80)  # Set bits 7 and 8.
            buffer.append((value >> 6) | 0x80)  # Set bit 8.
            buffer.append((value >> 13) | 0x80)  # Set bit 8.
            buffer.append(value >> 20)
        else:
            # Requires 5 bytes
            buffer.append(value | 0x40 | 0x80)  # Set bits 7 and 8.
            buffer.append((value >> 6) | 0x80)  # Set bit 8.
            buffer.append((value >> 13) | 0x80)  # Set bit 8.
            buffer.append((value >> 20) | 0x80)  # Set bit 8.
            buffer.append(value >> 27)

        return bytes(buffer)

class KeyStore:
    @staticmethod
    def prepare_tx (amount: float, to_address: str, from_address: str, last_ref: dict, fee: float = 0):
        if to_address == from_address:
          raise ValueError('KeyStore :: An address cannot send a transaction to itself')

        # normalize to integer and only preserve 8 decimals of precision
        amount = int((Decimal(amount) * Decimal(1e8)).quantize(Decimal('1.'), rounding=ROUND_DOWN))
        fee = int((Decimal(fee) * Decimal(1e8)).quantize(Decimal('1.'), rounding=ROUND_DOWN))

        if amount < 1e-8:
          raise ValueError('KeyStore :: Send amount must be greater than 1e-8')

        if fee < 0:
          raise ValueError('KeyStore :: Send fee must be greater or equal to zero')

        # Create transaction
        tx = TxEncode.get_tx_v2(amount, to_address, from_address, last_ref, fee)

        # Get encoded transaction
        encoded_tx = tx.get_encoded()


        serialized_tx = TxEncode().kryo_serialize(msg=encoded_tx, set_references=False)
        print("Serialized Tx:", serialized_tx)
        hash_value = hashlib.sha256(bytes.fromhex(serialized_tx)).hexdigest()



        return {
            "tx": tx.get_post_transaction(),
            "hash": hash_value,
            "rle": encoded_tx,
        }

    @staticmethod
    def sign(private_key_hex: hex, private_key_pem: bytes, tx_hash: hex):
        import subprocess

        # Prepare the command to execute the sign.mjs script with arguments
        command = [
            'node',
            '/home/mringdal/Development/pydag/signature.mjs',
            private_key_hex,
            tx_hash
        ]
        # Run the script and capture the result
        result = subprocess.run(command, capture_output=True, text=True)
        # Check if there was an error
        if result.returncode != 0:
            raise RuntimeError(f"Error in signing: {result.stderr}")

        # This is the non-dag4 signature:
        sig_new = result.stdout.strip()
        print("Non-DAG4 Signature:", sig_new)
        print("(Seems to sometimes fail, though it passes the dag4 verify)")
        # Prepare the command to execute the sign.mjs script with arguments
        command = [
            'node',
            '/home/mringdal/Development/pydag/sign.mjs',
            private_key_hex,
            tx_hash
        ]

        # Run the script and capture the result
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if there was an error
        if result.returncode != 0:
            raise RuntimeError(f"Error in signing: {result.stderr}")

        # This is the correct signature:
        print("Correct Signature:", result.stdout.strip())

        # Return the signature (result.stdout contains the signature in hex)
        #The return result ofcourse works:
        #return result.stdout.strip()
        return sig_new

    @staticmethod
    def verify(uncompressed_public_key, tx_hash, signature):
        import subprocess
        # Prepare the command to execute the sign.mjs script with arguments
        command = [
            'node',
            '/home/mringdal/Development/pydag/verify.mjs',
            uncompressed_public_key,
            tx_hash,
            signature
        ]

        # Run the script and capture the result
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if there was an error
        if result.returncode != 0:
            raise RuntimeError(f"Error in signing: {result.stderr}")

        # Return the signature (result.stdout contains the signature in hex)
        return result.stdout.strip()

def main():

    """Create wallet and test: This is done"""
    print("Step 1: Generating Keys and Address")
    bip39 = Bip39(); bip32 = Bip32(); wallet = Wallet()
    mnemonic_values = bip39.mnemonic()
    private_key = bip32.get_private_key_from_seed(seed_bytes=mnemonic_values["seed"])
    print("Private Key:", private_key.hex())
    public_key = bip32.get_public_key_from_private_hex(private_key_hex=private_key.hex())
    print("Public Key (Uncompressed):", public_key.hex())
    dag_addr = wallet.get_dag_address_from_public_key_hex(public_key_hex=public_key.hex())
    derived_seed = bip39.get_seed_from_mnemonic(words=mnemonic_values["words"])
    derived_private_key = bip32.get_private_key_from_seed(seed_bytes=derived_seed)
    derived_public_key = bip32.get_public_key_from_private_hex(private_key_hex=derived_private_key.hex())
    derived_dag_addr = wallet.get_dag_address_from_public_key_hex(public_key_hex=derived_public_key.hex())
    print("Success!" if derived_dag_addr == dag_addr else "Error!" and exit(1))
    print()

    """Get last reference"""
    print("Step 2: Get Last Reference (L1 LB)")
    endpoint = f"/transactions/last-reference/{dag_addr}"
    url = DEFAULT_L1_BASE_URL + endpoint

    # Make the POST request
    response = requests.get(url)

    # Print the response
    print("Status Code:", response.status_code)
    last_ref = response.json()
    print()

    """Generate signed transaction"""
    print("Step 3: Generate Transaction.")
    account = {"address": dag_addr, "public_key": PublicKey(bytes.fromhex(public_key.hex())), "private_key": PrivateKey(bytes.fromhex(private_key.hex()))}
    print(f"Account: {account}")
    print()

    amount = 1  # 1 DAG
    fee = 0.1  # Transaction fee
    from_address = dag_addr
    to_address = 'DAG4o8VYNg34Mnxp9mT4zDDCZTvrHWniscr3aAYv'
    last_ref = last_ref

    result = KeyStore.prepare_tx(amount, to_address, from_address, last_ref, fee)
    tx = result["tx"]
    tx_hash = result["hash"]
    print("Prepared Tx:", tx)
    print("Prepared Tx Hash:", tx_hash)
    print("Encoded Tx:", result["rle"])
    print()

    private_key_hex = account["private_key"].to_hex()
    private_key_pem = account["private_key"].to_pem()
    print("Private Key Hex:", private_key_hex)
    print("Private Key PEM:", private_key_pem)
    public_key_hex = account["public_key"].format(compressed=False).hex()
    signature = KeyStore.sign(private_key_hex=private_key_hex, private_key_pem=private_key_pem, tx_hash=tx_hash)
    print("Signature Returned by KeyStore.sign:", signature)
    print()
    success = KeyStore.verify(public_key_hex, tx_hash, signature)
    print("Verified by DAG4:", success.title())
    tx["proofs"].append({"id": public_key_hex[2:], "signature": signature})
    print("Tx to Post:", tx)

    """Post Transaction"""
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



