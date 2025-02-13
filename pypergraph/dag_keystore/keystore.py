from typing import Tuple

# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.serialization import load_pem_private_key
# from cryptography.x509 import CertificateBuilder, Name, NameAttribute, random_serial_number
# from cryptography.x509.oid import NameOID
# from cryptography.hazmat.primitives.serialization import (
#             Encoding,
#             PrivateFormat,
#             NoEncryption,
#         )
# from cryptography.hazmat.primitives.serialization import pkcs12

from ecdsa import SigningKey, SECP256k1, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der
from pyasn1.codec.der.decoder import decode as der_decode
from pyasn1.codec.der.encoder import encode as der_encode
from pyasn1.type.univ import Sequence, Integer

from .bip import Bip39, Bip32
from .tx_encode import TxEncode, TransactionV2
from pypergraph.dag_core.constants import PKCS_PREFIX

# import datetime
import hashlib
import base58


class KeyStore:
    """
    Methods dealing with keys.
    """

    PERSONAL_SIGN_PREFIX = "\u0019Constellation Signed Message:\n"
    DATA_SIGN_PREFIX = "\u0019Constellation Signed Data:\n"
    # @staticmethod
    # def get_p12_from_private_key(private_key: bytes, destination: str = "wallet.p12"):
    #     """
    #     Not in use for now.
    #
    #     :param private_key:
    #     :param destination:
    #     :return:
    #     """
    #     # Input: Private key PEM and optional certificate
    #
    #     sk = SigningKey.from_string(private_key, curve=SECP256k1)
    #     private_key_pem = sk.to_pem()
    #     private_key = load_pem_private_key(private_key_pem, password=None)
    #
    #     # Generate a self-signed certificate (optional)
    #     subject = issuer = Name([
    #         NameAttribute(NameOID.COMMON_NAME, u"Pypergraph Wallet v1"),
    #     ])
    #
    #     # Use timezone-aware UTC datetimes
    #     current_time = datetime.datetime.now(datetime.UTC)
    #     certificate = CertificateBuilder() \
    #         .subject_name(subject) \
    #         .issuer_name(issuer) \
    #         .public_key(private_key.public_key()) \
    #         .serial_number(random_serial_number()) \
    #         .not_valid_before(current_time) \
    #         .not_valid_after(current_time + datetime.timedelta(days=365 * 1000)) \
    #         .sign(private_key, hashes.SHA256())
    #
    #     # Create PKCS#12 archive
    #     p12_data = pkcs12.serialize_key_and_certificates(
    #         name=b"pypergraph_wallet",
    #         key=private_key,
    #         cert=certificate,
    #         cas=None,
    #         encryption_algorithm=NoEncryption()  # Use BestAvailableEncryption(b"password") for encrypted .p12
    #     )
    #
    #     # Save the .p12 file
    #     with open(destination, "wb") as p12_file:
    #         p12_file.write(p12_data)
    #
    # @staticmethod
    # def get_private_key_from_p12(destination: str = "wallet.p12", password: Optional[str] = None) -> str:
    #     """
    #     Not in use for now.
    #
    #     :param destination: Fullpath to the p12 file.
    #     :param password: Encrypt the p12 with password (default: None | unencrypted).
    #     :return: Private key as hex string.
    #     """
    #
    #     # Load the .p12 file
    #     with open(destination, "rb") as p12_file:
    #         p12_data = p12_file.read()
    #
    #     # Load PKCS#12 data
    #     private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
    #         p12_data, password
    #     )
    #
    #     # Extract the private key in PEM format
    #     if private_key:
    #         # Convert the private key to DER format
    #         private_key_der = private_key.private_bytes(
    #             encoding=Encoding.DER,
    #             format=PrivateFormat.PKCS8,
    #             encryption_algorithm=NoEncryption()
    #         )
    #
    #         # Use coincurve to load the private key and get its raw format
    #         sk = SigningKey.from_der(private_key)
    #         private_key_hex = sk.to_string().hex()
    #
    #         return private_key_hex
    #     else:
    #         raise ValueError("KeyStore :: No private key found in the .p12 file.")

    @staticmethod
    def prepare_tx (amount: int, to_address: str, from_address: str, last_ref: dict, fee: int = 0) -> Tuple[TransactionV2, str]:
        """
        Prepare a new transaction.

        :param amount: Amount to send.
        :param to_address: Destination DAG address.
        :param from_address: Source DAG address.
        :param last_ref: Dictionary with keys: ordinal, hash.
        :param fee: Transaction fee.
        :return: TransactionV2 object, sha512hash, rle.
        """
        if to_address == from_address:
          raise ValueError('KeyStore :: An address cannot send a transaction to itself')

        if amount < 1e-8:
          raise ValueError('KeyStore :: Send amount must be greater than 1e-8')

        if fee < 0:
          raise ValueError('KeyStore :: Send fee must be greater or equal to zero')

        # Create transaction
        tx = TxEncode.get_tx_v2(amount, to_address, from_address, last_ref, fee)

        # Get encoded transaction
        encoded_tx = tx.get_encoded()

        serialized_tx = TxEncode().kryo_serialize(msg=encoded_tx, set_references=False)
        hash_value = hashlib.sha512(hashlib.sha256(bytes.fromhex(serialized_tx)).hexdigest().encode("utf-8")).hexdigest()

        return tx, hash_value


    def data_sign(self, private_key, msg):
        message = f"{self.DATA_SIGN_PREFIX}{len(msg)}\n{msg}"
        # Serialize
        serialized_message = self.serialize(message)
        hash_value = hashlib.sha256(bytes.fromhex(serialized_message)).hexdigest()
        return self.sign(private_key, hash_value)


    @staticmethod
    def serialize(msg: str) -> str:
        return msg.encode("utf-8").hex()


    def personal_sign(self, msg, private_key):
        message = f"{self.PERSONAL_SIGN_PREFIX}{len(msg)}\n{msg}"
        return self.sign(private_key, message)


    @staticmethod
    def sign(private_key_hex: str, tx_hash: str) -> str:
        """
        Create transaction signature.

        :param private_key_hex: Private key in hex format.
        :param tx_hash: Transaction hash from prepare_tx.
        :return: Signature supported by the transaction API (@noble/secp256k1).
        """

        # secp256k1 curve order
        SECP256K1_ORDER = SECP256k1.order

        def _enforce_canonical_signature(signature: bytes) -> bytes:
            """
            Adjust the signature to ensure canonical form (s < curve_order / 2).
            """
            r, s = _decode_der(signature)
            if s > SECP256K1_ORDER // 2:
                s = SECP256K1_ORDER - s
            return _encode_der(r, s)

        def _decode_der(signature: bytes):
            """
            Decode a DER-encoded signature to (r, s).
            """
            seq, _ = der_decode(signature, asn1Spec=Sequence())
            r = int(seq[0])
            s = int(seq[1])
            return r, s

        def _encode_der(r: int, s: int) -> bytes:
            """
            Encode (r, s) back into DER format.
            """
            seq = Sequence()
            seq.setComponentByPosition(0, Integer(r))
            seq.setComponentByPosition(1, Integer(s))
            return der_encode(seq)

        def _sign_deterministic_canonical(private_key_hex: str, tx_hash: bytes) -> str:
            """
            Create a deterministic and canonical secp256k1 signature.
            """
            # Create SigningKey object from private key hex
            sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)

            # Sign the prehashed message deterministically
            signature_der = sk.sign_digest_deterministic(
                tx_hash[:32],  # Truncate to 32 bytes if needed
                hashfunc=hashlib.sha256,
                sigencode=sigencode_der,
            )

            canonical_signature_der = _enforce_canonical_signature(signature_der)
            return canonical_signature_der.hex()

        return _sign_deterministic_canonical(private_key_hex=private_key_hex, tx_hash=bytes.fromhex(tx_hash))

    @staticmethod
    def verify(public_key_hex, tx_hash, signature_hex) -> bool:
        """
        Verify is the signature is valid.

        :param public_key_hex:
        :param tx_hash: Hex format
        :param signature_hex:
        :return: True or False
        """

        vk = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
        try:
            # Use verify_digest for prehashed input
            valid = vk.verify_digest(
                bytes.fromhex(signature_hex),
                bytes.fromhex(tx_hash)[:32],  # Prehashed hash
                sigdecode=sigdecode_der
            )
            return valid
        except Exception:
            return False

    @staticmethod
    def verify_data():
        pass

    @staticmethod
    def validate_address(address: str) -> bool:
        if not address:
            return False

        valid_len = len(address) == 40
        valid_prefix = address.startswith("DAG")
        valid_parity = address[3].isdigit() and 0 <= int(address[3]) < 10
        base58_part = address[4:]
        valid_base58 = (
            len(base58_part) == 36 and base58_part == base58.b58encode(base58.b58decode(base58_part)).decode()
        )

        return valid_len and valid_prefix and valid_parity and valid_base58

    @staticmethod
    def validate_mnemonic(mnemonic_phrase: str) -> bool:
        """
        Validate mnemonic seed phrase.

        :param mnemonic_phrase: String of words (default: 12).
        :return: Boolean value.
        """

        return Bip39.validate_mnemonic(mnemonic_phrase=mnemonic_phrase)


    @staticmethod
    def get_mnemonic() -> dict:
        """
        :return: Mnemonic values in a dictionary with keys: mnemo, words, seed, entropy
        """
        bip39 = Bip39()
        return bip39.mnemonic()

    @staticmethod
    def get_private_key_from_mnemonic(phrase: str) -> str:
        """
        Get private key from mnemonic seed (not phrase)

        :param seed:
        :return: Private key as hexadecimal string
        """
        bip32 = Bip32()
        bip39 = Bip39()
        seed = bip39.get_seed_from_mnemonic(phrase)
        private_key =  bip32.get_private_key_from_seed(seed_bytes=seed)
        return private_key.hex()

    @staticmethod
    def get_public_key_from_private(private_key: str) -> str:
        """
        :param private_key:
        :return: Public key (Node ID)
        """
        bip32 = Bip32()
        return bip32.get_public_key_from_private_hex(private_key_bytes=bytes.fromhex(private_key))

    @staticmethod
    def get_dag_address_from_public_key(public_key_hex: str) -> str:
        """
        :param public_key_hex: The private key as a hexadecimal string.
        :return: The DAG address corresponding to the public key (node ID).
        """
        if len(public_key_hex) == 128:
            public_key = PKCS_PREFIX + "04" + public_key_hex
        elif len(public_key_hex) == 130 and public_key_hex[:2] == "04":
            public_key = PKCS_PREFIX + public_key_hex
        else:
            raise ValueError("KeyStore :: Not a valid public key.")

        public_key = hashlib.sha256(bytes.fromhex(public_key)).hexdigest()
        public_key = base58.b58encode(bytes.fromhex(public_key)).decode()
        public_key = public_key[len(public_key) - 36:]

        check_digits = "".join([char for char in public_key if char.isdigit()])
        check_digit = 0
        for n in check_digits:
            check_digit += int(n)
            if check_digit >= 9:
                check_digit = check_digit % 9

        address = f"DAG{check_digit}{public_key}"

        return address

