import binascii
import hashlib
from binascii import hexlify
from decimal import Decimal, ROUND_DOWN

import subprocess
import sys
import os

import secp256k1
from coincurve import PrivateKey, PublicKey
from coincurve.ecdsa import recoverable_convert, deserialize_recoverable

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
    def private_key_to_p12(private_key):
        from cryptography.hazmat.primitives.serialization import (
            pkcs12,
            Encoding,
            PrivateFormat,
            NoEncryption,
        )
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        from cryptography.x509 import CertificateBuilder, Name, NameAttribute, random_serial_number
        from cryptography.x509.oid import NameOID
        import datetime

        # Input: Private key PEM and optional certificate
        private_key_pem = PrivateKey(private_key).to_pem()
        private_key = load_pem_private_key(private_key_pem, password=None)

        # Generate a self-signed certificate (optional)
        subject = issuer = Name([
            NameAttribute(NameOID.COMMON_NAME, u"My Name"),
        ])

        # Use timezone-aware UTC datetimes
        current_time = datetime.datetime.now(datetime.UTC)
        certificate = CertificateBuilder() \
            .subject_name(subject) \
            .issuer_name(issuer) \
            .public_key(private_key.public_key()) \
            .serial_number(random_serial_number()) \
            .not_valid_before(current_time) \
            .not_valid_after(current_time + datetime.timedelta(days=365 * 1000)) \
            .sign(private_key, hashes.SHA256())

        # Create PKCS#12 archive
        p12_data = pkcs12.serialize_key_and_certificates(
            name=b"MyKey",
            key=private_key,
            cert=certificate,
            cas=None,
            encryption_algorithm=NoEncryption()  # Use BestAvailableEncryption(b"password") for encrypted .p12
        )

        # Save the .p12 file
        with open("my_certificate.p12", "wb") as p12_file:
            p12_file.write(p12_data)

        print("PKCS#12 file created as my_certificate.p12")

    @staticmethod
    def private_key_from_p12():
        from cryptography.hazmat.primitives.serialization import pkcs12

        # Load the .p12 file
        with open("my_certificate.p12", "rb") as p12_file:
            p12_data = p12_file.read()

        # Load PKCS#12 data
        password = None  # Replace with the password if the .p12 is encrypted
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            p12_data, password
        )

        # Extract the private key in PEM format
        if private_key:
            # Convert the private key to DER format
            private_key_der = private_key.private_bytes(
                encoding=Encoding.DER,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            )

            # Use coincurve to load the private key and get its raw format
            coincurve_key = PrivateKey.from_der(private_key_der)
            private_key_hex = coincurve_key.to_hex()

            # Print or use the raw private key
            print(f"Raw private key (hex): {private_key_hex}")

            # Convert to bytes if needed
            private_key_bytes = bytes.fromhex(private_key_hex)
            print(f"Raw private key (bytes): {private_key_bytes}")
            return private_key_hex
        else:
            print("No private key found in the .p12 file.")

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
    def sign(private_key_hex: hex, tx_hash: hex):

        pk = secp256k1.PrivateKey(bytes.fromhex(private_key_hex))
        recoverable_sig = pk.ecdsa_sign(hashlib.sha512(tx_hash.encode('utf-8')).digest())
        der_sig = pk.ecdsa_serialize(recoverable_sig)
        print("DER Sig:", hexlify(der_sig))


        import subprocess

        # Prepare the command to execute the sign.mjs script with arguments
        command = [
            'node',
            '/home/mringdal/Development/pydag/sign.bundle.js',
            private_key_hex,
            hashlib.sha512(tx_hash.encode('utf-8')).hexdigest()
        ]
        # Run the script and capture the result
        result = subprocess.run(command, capture_output=True, text=True)
        # Check if there was an error
        if result.returncode != 0:
            raise RuntimeError(f"Error in signing: {result.stderr}")

        sig = result.stdout.strip()

        return sig


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

    KeyStore.private_key_to_p12(account["private_key"].secret)

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

    print("Private Key Hex:", private_key_hex)
    public_key_hex = account["public_key"].format(compressed=False).hex()
    signature = KeyStore.sign(private_key_hex=private_key_hex, tx_hash=tx_hash)
    print("Signature Returned by KeyStore.sign:", signature)
    print()
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



