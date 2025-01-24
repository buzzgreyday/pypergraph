from abc import ABC, abstractmethod

import base58
import hashlib

from typing import List, Optional, Dict, Any

from eth_keys import keys
from eth_utils import to_checksum_address, is_checksum_address, keccak
from typing import List

from ecdsa import SigningKey, SECP256k1

from pypergraph.dag_core import KeyringAssetType, KeyringNetwork
from pypergraph.dag_core.constants import PKCS_PREFIX



class EcdsaAccount(ABC):
    def __init__(self):
        self.tokens: Optional[List[str]] = None
        self.wallet: Optional[SigningKey] = None
        self.assets: Optional[List[Any]] = None
        self.bip44_index: Optional[int] = None
        self.provider = None  # Placeholder for Web3 provider
        self._label: Optional[str] = None

    @property
    @abstractmethod
    def decimals(self) -> int:
        pass

    @property
    @abstractmethod
    def network(self) -> str:
        pass

    @property
    @abstractmethod
    def has_token_support(self) -> bool:
        pass

    @property
    @abstractmethod
    def supported_assets(self) -> List[str]:
        pass

    @abstractmethod
    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        pass

    def get_decimals(self) -> int:
        return self.decimals

    def get_label(self) -> str:
        return self._label

    def create(self, private_key: Optional[str]):
        if private_key:
            self.wallet = SigningKey.from_string(private_key, curve=SECP256k1)
        else:
            self.wallet = SigningKey.generate(curve=SECP256k1)
        return self

    def save_token_info(self, address: str):
        pass

    def get_web3_provider(self):
        return self._provider

    def set_web3_provider(self, provider):
        self._provider = provider

    def get_tokens(self) -> Optional[List[str]]:
        return self.tokens.copy() if self.tokens else None

    def set_tokens(self, tokens: List[str]):
        if tokens:
            self.tokens = tokens.copy()

    def get_bip44_index(self) -> Optional[int]:
        return self.bip44_index

    def get_state(self) -> Dict[str, Any]:
        result = {
            "address": self.get_address(),
            "supportedAssets": self.supported_assets,
        }
        if self._label:
            result["label"] = self._label
        if self.tokens:
            result["tokens"] = self.tokens
        return result

    def get_network(self):
        return self.network

    def serialize(self, include_private_key: bool = True) -> Dict[str, Any]:
        result = {}
        if include_private_key:
            result["privateKey"] = self.get_private_key()
        if self._label:
            result["label"] = self._label
        if self.tokens:
            result["tokens"] = self.tokens.copy()
        if self.bip44_index is not None:
            result["bip44Index"] = self.bip44_index
        return result

    def deserialize(self, data: Dict[str, Any]):

        private_key = bytes.fromhex(data.get("privateKey"))
        public_key = data.get("publicKey")
        tokens = data.get("tokens")
        bip44_index = data.get("bip44Index")
        label = data.get("label")

        if private_key:
            self.wallet = SigningKey.from_string(private_key, curve=SECP256k1)
        else:
            raise NotImplementedError("EcdsaAccount :: Wallet instance from public key isn't supported.")
            # TODO: This doesn't work since the library doens't seem to have any equivalent
            #self.wallet = Wallet.from_public_key(bytes.fromhex(public_key))

        self._label = label
        self.bip44_index = bip44_index
        self.tokens = tokens or self.tokens
        return self

    # def sign_message(self, msg: str) -> str:
    #     private_key = self.get_private_key_buffer()
    #     msg_hash = eth_util.hash_personal_message(msg.encode())
    #
    #     v, r, s = eth_util.ecsign(msg_hash, private_key)
    #
    #     if not eth_util.is_valid_signature(v, r, s):
    #         raise ValueError("Sign-Verify failed")
    #
    #     return eth_util.strip_hex_prefix(eth_util.to_rpc_sig(v, r, s))

    def recover_signed_msg_public_key(self, msg: str, signature: str) -> str:
        # Compute the hash of the message in Ethereum's personal_sign format
        msg_hash = keccak(text=f"\x19Ethereum Signed Message:\n{len(msg)}{msg}")

        # Decode the signature (remove '0x' prefix if present)
        signature_bytes = bytes.fromhex(signature[2:] if signature.startswith("0x") else signature)
        v, r, s = signature_bytes[-1], signature_bytes[:32], signature_bytes[32:64]

        # Recover the public key
        try:
            public_key = keys.ecdsa_recover(msg_hash,
                                            keys.Signature(vrs=(v, int.from_bytes(r, 'big'), int.from_bytes(s, 'big'))))
        except Exception as e:
            raise ValueError(f"EcdsaAccount :: Failed to recover public key: {e}")

        # Return the public key in hexadecimal format
        return public_key.to_hex()

    def get_address(self) -> str:
        #return self.wallet.get_checksum_address_string()
        vk = self.wallet.get_verifying_key().to_string()

        # Compute the keccak hash of the public key (last 20 bytes is the address)
        public_key = b"\x04" + vk  # Add the uncompressed prefix
        address = keccak(public_key[1:])[-20:]  # Drop the first byte (x-coord prefix)

        return to_checksum_address("0x" + address.hex())

    def get_public_key(self) -> str:
        return self.wallet.get_verifying_key().to_string().hex()

    def get_private_key(self) -> str:
        return self.wallet.to_string().hex()

    def get_private_key_buffer(self):
        return self.wallet.to_string()


class EthAccount(EcdsaAccount):
    decimals = 18
    network = KeyringNetwork.Ethereum.value
    has_token_support = True
    supported_assets = [KeyringAssetType.ETH.value, KeyringAssetType.ERC20.value]
    tokens = ["0xa393473d64d2F9F026B60b6Df7859A689715d092"]  # LTX

    def save_token_info(self, address: str):
        """Save the token info if not already present in the tokens list."""
        if address not in self.tokens:
            self.tokens.append(address)

    def validate_address(self, address: str) -> bool:
        """Validate an Ethereum address."""
        return is_checksum_address(address)

    def sign_transaction(self, tx):
        """
        Sign an Ethereum transaction with the account's private key.

        tx is an instance of the transaction object from a library like web3.eth.account.
        """
        priv_key = self.get_private_key_buffer()
        signed_tx = tx.sign(priv_key)
        return signed_tx

    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        """Verify if a signed message matches the provided address."""
        public_key = self.recover_signed_msg_public_key(msg, signature)
        actual_address = self.get_address_from_public_key(public_key)
        return to_checksum_address(says_address) == actual_address

    def get_address_from_public_key(self, public_key: str) -> str:
        """Derive the Ethereum address from the public key."""
        address = b"\x04" + hashlib.sha3_256(public_key.encode("utf-8")).digest()
        return to_checksum_address(address)

    def get_encryption_public_key(self) -> str:
        """Get the public key for encryption."""
        # This is a placeholder. Replace it with the appropriate implementation.
        # For example, if using web3py, you can use `eth_account.Account.encrypt()` for encryption keys.
        raise NotImplementedError("Encryption public key generation is not yet implemented.")


class DagAccount(EcdsaAccount):

    decimals = 8
    network = KeyringNetwork.Constellation.value  # Equivalent to `KeyringNetwork.Constellation`
    has_token_support = False
    supported_assets = ["DAG"]  # Can be found among keyring assets in DAG4
    tokens = None  # Placeholder for default assets

    def sign_transaction(self, tx):
        # Implement transaction signing logic here if needed
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

    def get_public_key(self) -> str:
        return self.wallet.get_verifying_key().to_string().hex()

    def get_address(self) -> str:
        return self.get_address_from_public_key(self.get_public_key())

    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        public_key = self.recover_signed_msg_public_key(msg, signature)
        actual_address = self.get_address_from_public_key(public_key)
        return says_address == actual_address

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def get_address_from_public_key(self, public_key_hex: str) -> str:
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

