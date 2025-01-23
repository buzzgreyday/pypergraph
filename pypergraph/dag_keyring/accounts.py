import base58
import hashlib

from typing import List, Optional, Dict, Any

from eth_account import Account
from eth_account.messages import encode_defunct

from pypergraph.dag_core import KeyringAssetType, KeyringNetwork


class EcdsaAccount:
    def __init__(self):
        self.tokens: Optional[List[str]] = None
        self.wallet = None  # Placeholder for Wallet instance
        self.assets: Optional[List[Any]] = None
        self.bip44_index: Optional[int] = None
        self.decimals = 18 # Should be set dynamically
        self.supported_assets = [KeyringAssetType.ETH.value] # Assets can be found in accounts dir, DAG4
        self.network = KeyringNetwork.Ethereum.value
        self.has_token_support = False
        self._provider = None
        self._label = None

    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        message = encode_defunct(text=msg)
        recovered_address = Account.recover_message(message, signature=signature)
        return recovered_address.lower() == says_address.lower()

    def get_decimals(self) -> int:
        return self.decimals

    def get_label(self) -> str:
        return self._label

    def create(self, private_key: Optional[str]):
        if private_key:
            self.wallet = Account.from_key(bytes.fromhex(private_key))
        else:
            self.wallet = Account.create()
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
        private_key = data.get("privateKey")
        public_key = data.get("publicKey")
        tokens = data.get("tokens")
        bip44_index = data.get("bip44Index")
        label = data.get("label")

        if private_key:
            self.wallet = Account.from_key(private_key)
            #self.wallet = "THIS_IS_NOT_A_PRIVATE_KEY_WALLET"
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

    # def recover_signed_msg_public_key(self, msg: str, signature: str) -> str:
    #     msg_hash = eth_util.hash_personal_message(msg.encode())
    #     signature_params = eth_util.from_rpc_sig("0x" + signature)
    #     public_key_buffer = eth_util.ecrecover(
    #         msg_hash, signature_params.v, signature_params.r, signature_params.s
    #     )
    #     return public_key_buffer.hex()

    def get_address(self) -> str:
        return self.wallet.get_checksum_address_string()

    def get_public_key(self) -> str:
        return self.wallet.get_public_key().hex()

    def get_private_key(self) -> str:
        return self.wallet.get_private_key().hex()

    def get_private_key_buffer(self):
        return self.wallet.get_private_key()

class DagAccount(EcdsaAccount):
    def __init__(self):
        super().__init__()
        self.decimals = 8
        self.network = KeyringNetwork.Constellation.value  # Equivalent to `KeyringNetwork.Constellation`
        self.has_token_support = False
        self.supported_assets = ["DAG"]  # Can be found among keyring assets in DAG4
        self.tokens = None  # Placeholder for default assets

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
        if len(public_key_hex) == 128:
            public_key_hex = "04" + public_key_hex

        pkcs_prefix = "3056301006072a8648ce3d020106052b8104000a034200"
        public_key_hex = pkcs_prefix + public_key_hex

        sha256_str = self.sha256(bytes.fromhex(public_key_hex))
        bytes_hash = bytes.fromhex(sha256_str)
        base58_encoded = base58.b58encode(bytes_hash).decode()

        end = base58_encoded[-36:]
        sum_digits = sum(int(char) for char in end if char.isdigit())
        par = sum_digits % 9

        return f"DAG{par}{end}"