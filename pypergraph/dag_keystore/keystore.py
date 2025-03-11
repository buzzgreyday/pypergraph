import base64
import hashlib
import json
import random

import aiopath
import eth_keyfile
from decimal import Decimal
from typing import Tuple, Callable, Optional, Union, Literal, Dict, Any

import base58

from ecdsa import SigningKey, SECP256k1, VerifyingKey
from ecdsa.util import sigencode_der, sigdecode_der
from pyasn1.codec.der.decoder import decode as der_decode
from pyasn1.codec.der.encoder import encode as der_encode
from pyasn1.type.univ import Sequence, Integer

from pypergraph.dag_core.constants import PKCS_PREFIX
from pypergraph.dag_network.models.account import LastReference
from pypergraph.dag_network.models.transaction import Transaction
from .bip import Bip39, Bip32
from .kryo import Kryo
from .v3_keystore import V3KeystoreCrypto, V3Keystore

MIN_SALT = int(Decimal("1e8"))

class KeyStore:
    """
    Methods dealing with keys.
    """

    PERSONAL_SIGN_PREFIX = "\u0019Constellation Signed Message:\n"
    DATA_SIGN_PREFIX = "\u0019Constellation Signed Data:\n"

    @staticmethod
    def prepare_tx(
            amount: int,
            to_address: str,
            from_address: str,
            last_ref: LastReference,
            fee: int = 0
    ) -> Tuple[Transaction, str]:
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

        if int(amount) < 1e-8:
          raise ValueError('KeyStore :: Send amount must be greater than 1e-8')

        if fee < 0:
          raise ValueError('KeyStore :: Send fee must be greater or equal to zero')

        # Create transaction
        tx = Transaction(
            source=from_address, destination=to_address, amount=amount, fee=fee,
            parent=last_ref, salt=MIN_SALT + int(random.getrandbits(48))
        )

        # Get encoded transaction
        encoded_tx = tx.encoded

        kryo = Kryo()
        serialized_tx = kryo.serialize(msg=encoded_tx, set_references=False)
        hash_value = hashlib.sha256(bytes.fromhex(serialized_tx)).hexdigest()

        return tx, hash_value

    def _encode_data(self, encoding, prefix, msg):
        if encoding:
            if callable(encoding):
                # Use custom encoding function
                msg = encoding(msg)
            elif encoding == "base64":
                # Used in the VOTING and NFT metagraph example
                encoded = json.dumps(msg, separators=(',', ':'))
                msg = base64.b64encode(encoded.encode()).decode()
            elif encoding == "hex":
                # Used in the TO-DO, SOCIAL and WATER AND ENERGY metagraph example
                msg = json.dumps(msg, separators=(',', ':'))
        else:
            # Default: used in the TO-DO, SOCIAL and WATER AND ENERGY metagraph examples
            msg = json.dumps(msg, separators=(',', ':'))

        if prefix:
            msg = f"{self.DATA_SIGN_PREFIX}{len(msg)}\n{msg}"
        return msg

    def data_sign(
            self,
            private_key,
            msg: dict,
            prefix: bool = True,
            encoding: Optional[Union[Literal["hex", "base64"], Callable[[dict], str], None]] = None
    ) -> Tuple[str, str]:
        """
        Encode message according to serializeUpdate on your template module l1.

        :param private_key:
        :param msg:
        :param prefix:
        :param encoding:
        :return:
        """

        # 1. The TO-DO, SOCIAL and WATER AND ENERGY template doesn't add the signing prefix, it only needs the transaction to be formatted as string without spaces and None values:
        #     # encoded = json.dumps(tx_value, separators=(',', ':'))
        #     signature, hash_ = keystore.data_sign(pk, encoded, prefix=False) # Default encoding = "hex"
        # 2. The VOTING and NFT template does use the dag4JS dataSign (prefix=True), the encoding (before data_sign) is done first by stringifying, then converting to base64:
        #     # encoded = json.dumps(tx_value, separators=(',', ':'))
        #     # encoded = base64.b64encode(encoded.encode()).decode()
        #     signature, hash_ = keystore.data_sign(pk, tx_value, prefix=True, encoding="base64") # Default prefix is True
        # 3. The TO-DO, SOCIAL and WATER AND ENERGY template doesn't add the signing prefix, it only needs the transaction to be formatted as string without spaces and None values:
        #     # encoded = json.dumps(tx_value, separators=(',', ':'))
        #     signature, hash_ = keystore.data_sign(pk, encoded, prefix=False) # Default encoding = "hex"
        # X. Inject a custom encoding function:
        #     def encode(msg: dict):
        #         return json.dumps(tx_value, separators=(',', ':'))
        #
        #     signature, hash_ = keystore.data_sign(pk, tx_value, prefix=False, encoding=encode)

        msg = self._encode_data(encoding=encoding, prefix=prefix, msg=msg)

        """ Serialize """
        serialized = msg.encode('utf-8')

        hash_ = hashlib.sha256(serialized).hexdigest()
        """ Sign """
        signature = self.sign(private_key, hash_)
        return signature, hash_

    #def serialize(self, msg: str):
    #    return msg.encode("utf-8").hex()

    def personal_sign(self, msg, private_key) -> str:
        # TODO: How is this used?
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

        tx_hash = hashlib.sha512(tx_hash.encode("utf-8")).digest()

        return _sign_deterministic_canonical(private_key_hex=private_key_hex, tx_hash=tx_hash)

    @staticmethod
    def verify(public_key_hex, tx_hash, signature_hex) -> bool:
        """
        Verify is the signature is valid.

        :param public_key_hex:
        :param tx_hash: Hex format
        :param signature_hex:
        :return: True or False
        """
        tx_hash = hashlib.sha512(tx_hash.encode("utf-8")).digest()
        vk = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
        try:
            # Use verify_digest for prehashed input
            valid = vk.verify_digest(
                bytes.fromhex(signature_hex),
                tx_hash[:32],  # Prehashed hash
                sigdecode=sigdecode_der
            )
            return valid
        except Exception:
            return False

    @staticmethod
    def verify_data(public_key: str, msg: str, signature: str):
        # TODO
        pass


    @staticmethod
    def validate_address(address: str) -> bool:
        """
        Returns True if DAG address is valid, False if invalid.

        :param address: DAG address.
        :return: Boolean value.
        """
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
        Returns True is phrase is valid, False if invalid.

        :param mnemonic_phrase: String of words (default: 12).
        :return: Boolean value.
        """

        return Bip39.validate_mnemonic(mnemonic_phrase=mnemonic_phrase)


    @staticmethod
    def get_mnemonic() -> str:
        """
        :return: Mnemonic values in a dictionary with keys: mnemo, words, seed, entropy
        """
        bip39 = Bip39()
        return bip39.mnemonic()

    def generate_private_key(self) -> str:
        """
        Generates private key.

        :return: Private key hex.
        """
        return SigningKey.generate(SECP256k1).to_string().hex()

    @staticmethod
    async def encrypt_keystore_from_phrase(phrase: str, password: str):
        """Probably used if inactive for some time"""
        return await V3KeystoreCrypto.encrypt_phrase(phrase=phrase, password=password)

    @staticmethod
    async def encrypt_keystore_from_private_key(private_key: Optional[str], password: str = '') -> V3Keystore:
        """Probably used if inactive for some time"""
        return await V3KeystoreCrypto.encrypt_phrase(phrase=private_key, password=password)

    @staticmethod
    async def decrypt_keystore_private_key(keystore: V3Keystore, password: str = ''):
        """Probably used if inactive for some time"""
        return await V3KeystoreCrypto.decrypt_phrase(keystore=keystore, password=password)

    @staticmethod
    def get_extended_private_key_from_mnemonic(mnemonic: str):
        # Extended keys can be used to derive child keys
        bip39 = Bip39()
        bip32 = Bip32()
        if bip39.validate_mnemonic(mnemonic):
            seed_bytes = bip39.get_seed_from_mnemonic(mnemonic)
            root_key = bip32.get_root_key_from_seed(seed_bytes)
            # TODO check this
            return root_key.ExtendedKey()

    @staticmethod
    def get_private_key_from_mnemonic(phrase: str) -> str:
        """
        Get private key from mnemonic seed (not phrase)

        :param phrase:
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

