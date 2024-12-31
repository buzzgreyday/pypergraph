from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import CertificateBuilder, Name, NameAttribute, random_serial_number
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import (
            pkcs12,
            Encoding,
            PrivateFormat,
            NoEncryption,
        )
from cryptography.hazmat.primitives.serialization import pkcs12
from coincurve import PrivateKey, PublicKey
from decimal import Decimal, ROUND_DOWN

from .bip import Bip39, Bip32
from .tx_encode import TxEncode
from dag_wallet import Wallet

import datetime
import hashlib

class KeyStore:
    @staticmethod
    def get_p12_from_private_key(private_key: bytes, destination: str = "wallet.p12"):
        # Input: Private key PEM and optional certificate
        private_key_pem = PrivateKey(private_key).to_pem()
        private_key = load_pem_private_key(private_key_pem, password=None)

        # Generate a self-signed certificate (optional)
        subject = issuer = Name([
            NameAttribute(NameOID.COMMON_NAME, u"Pypergraph Wallet v1"),
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
            name=b"pypergraph_wallet",
            key=private_key,
            cert=certificate,
            cas=None,
            encryption_algorithm=NoEncryption()  # Use BestAvailableEncryption(b"password") for encrypted .p12
        )

        # Save the .p12 file
        with open(destination, "wb") as p12_file:
            p12_file.write(p12_data)

    @staticmethod
    def get_private_key_from_p12(destination: str = "wallet.p12", password: str | None = None):
        """
        :param destination: Fullpath to the p12 file
        :param password: Encrypt the p12 with password (default: None | unencrypted)
        :return: Private key as hex string
        """

        # Load the .p12 file
        with open(destination, "rb") as p12_file:
            p12_data = p12_file.read()

        # Load PKCS#12 data
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

            return private_key_hex
        else:
            raise ValueError("No private key found in the .p12 file.")

    @staticmethod
    def prepare_tx (amount: float, to_address: str, from_address: str, last_ref: dict, fee: float = 0):
        """
        :param amount: Amount to send
        :param to_address: Destionation DAG address
        :param from_address: Source DAG address
        :param last_ref: Dictionary with keys: ordinal, hash
        :param fee: Transaction fee
        :return: Dictionary with keys: tx, hash, rle
        """
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
        hash_value = hashlib.sha256(bytes.fromhex(serialized_tx)).hexdigest()



        return {
            "tx": tx.get_post_transaction(),
            "hash": hash_value,
            "rle": encoded_tx,
        }

    @staticmethod
    def sign(private_key_hex: str, tx_hash: str) -> str:
        """
        Signs DAG transaction using JavaScript
        :param private_key_hex: Private key in hex format
        :param tx_hash: Transaction hash from prepare_tx
        :return: Signature supported by the transaction API (@noble/secp256k1 | Bouncy Castle)
        """
        import subprocess

        # Prepare the command to execute the sign.mjs script with arguments
        command = [
            'node',
            '/home/mringdal/Development/pydag/js/sign.bundle.js',
            private_key_hex,
            hashlib.sha512(tx_hash.encode('utf-8')).hexdigest()
        ]
        # Run the script and capture the result
        result = subprocess.run(command, capture_output=True, text=True)
        # Check if there was an error
        if result.returncode != 0:
            raise RuntimeError(f"Error in signing: {result.stderr}")

        signature = result.stdout.strip()

        return signature

    @staticmethod
    def get_mnemonic() -> dict:
        """Returns mnemonic values in a dictionary with keys: mnemo, words, seed, entropy"""
        bip39 = Bip39()
        return bip39.mnemonic()

    @staticmethod
    def get_private_key_from_seed(seed: bytes) -> bytes:
        """Returns private key in bytes"""
        bip32 = Bip32()
        return bip32.get_private_key_from_seed(seed_bytes=seed)

    @staticmethod
    def get_public_key_from_private_key(private_key: hex) -> bytes:
        """Returns the public key in bytes"""
        bip32 = Bip32()
        return bip32.get_public_key_from_private_hex(private_key_hex=private_key)

    @staticmethod
    def get_dag_address_from_public_key(public_key: str) -> str:
        """Returns DAG address as string"""
        wallet = Wallet()
        return wallet.get_dag_address_from_public_key_hex(public_key_hex=public_key)