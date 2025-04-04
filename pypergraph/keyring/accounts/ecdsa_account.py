from abc import ABC, abstractmethod
from typing import Optional, List, Any, Dict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from eth_utils import keccak, to_checksum_address
from eth_keys import keys
from pydantic import BaseModel, Field, ConfigDict


class EcdsaAccount(BaseModel, ABC):
    tokens: List[str] = Field(default_factory=list)
    wallet: Optional[ec.EllipticCurvePrivateKey] = None
    assets: List[Any] = Field(default_factory=list)
    bip44_index: Optional[int] = None
    provider: Any = None
    label: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    @abstractmethod
    def decimals(self) -> int:
        pass

    @property
    @abstractmethod
    def network_id(self) -> str:
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
        return self.label

    def create(self, private_key: Optional[str]):
        if private_key:
            # Convert hex private key to cryptography object
            private_key_bytes = bytes.fromhex(private_key)
            private_key_int = int.from_bytes(private_key_bytes, byteorder='big')
            self.wallet = ec.derive_private_key(
                private_value=private_key_int, curve=ec.SECP256K1(), backend=default_backend()
            )
        else:
            self.wallet = ec.generate_private_key(curve=ec.SECP256K1(), backend=default_backend())
        return self

    def save_token_info(self, address: str):
        pass

    def get_web3_provider(self):
        return self._provider

    def set_web3_provider(self, provider):
        self._provider = provider

    def get_tokens(self) -> Optional[List[str]]:
        return self.tokens.copy() if self.tokens else []

    def set_tokens(self, tokens: List[str]):
        if tokens:
            self.tokens = tokens.copy()

    def get_bip44_index(self) -> Optional[int]:
        return self.bip44_index

    def get_state(self) -> Dict[str, Any]:
        result = {
            "address": self.get_address(),
            "supported_assets": self.supported_assets,
        }
        if self.label:
            result["label"] = self.label
        if self.tokens:
            result["tokens"] = self.tokens
        return result

    def get_network_id(self):
        return self.network_id

    def serialize(self, include_private_key: bool = True) -> Dict[str, Any]:
        result = {}
        if include_private_key:
            result["private_key"] = self.get_private_key()
        if self.label:
            result["label"] = self.label
        if self.tokens:
            result["tokens"] = self.tokens.copy()
        if self.bip44_index is not None:
            result["bip44_index"] = self.bip44_index
        return result

    def deserialize(
            self, bip44_index: Optional[int] = None, label: Optional[str] = None,
            private_key: Optional[str] = None, public_key: Optional[str] = None, tokens: Optional[List[str]] = None
    ):

        self.label = label
        self.bip44_index = bip44_index
        self.tokens = tokens or self.tokens

        if private_key:
            # Convert hex private key to cryptography object
            private_key_bytes = bytes.fromhex(private_key)
            private_key_int = int.from_bytes(private_key_bytes, byteorder='big')
            self.wallet = ec.derive_private_key(
                private_value=private_key_int, curve=ec.SECP256K1(), backend=default_backend()
            )
        else:
            raise NotImplementedError("EcdsaAccount :: Wallet instance from public key isn't supported.")
            # TODO: This doesn't work since the library doens't seem to have any equivalent

        return self

    # TODO
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
        public_key = self.wallet.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )

        # Take keccak of everything except the first byte (0x04)
        address = keccak(public_bytes[1:])[-20:]

        return to_checksum_address("0x" + address.hex())

    def get_public_key(self) -> str:
        public_key = self.wallet.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        return public_bytes.hex()

    def get_private_key(self) -> str:
        private_bytes = self.wallet.private_numbers().private_value.to_bytes(32, 'big')
        return private_bytes.hex()

    def get_private_key_buffer(self):
        return self.wallet.private_numbers().private_value.to_bytes(32, 'big')