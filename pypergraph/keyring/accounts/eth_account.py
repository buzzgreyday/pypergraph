from typing import List

from eth_utils import to_checksum_address
from pydantic import Field

from pypergraph.core import NetworkId, KeyringAssetType
from .ecdsa_account import EcdsaAccount


class EthAccount(EcdsaAccount):
    @property
    def decimals(self) -> int:
        return 18

    @property
    def network_id(self) -> str:
        return NetworkId.Ethereum.value

    @property
    def has_token_support(self) -> bool:
        return True

    @property
    def supported_assets(self) -> List[str]:
        return [KeyringAssetType.ETH.value, KeyringAssetType.ERC20.value]

    tokens: List[str] = Field(default=["0xa393473d64d2F9F026B60b6Df7859A689715d092"])

    def save_token_info(self, address: str):
        """Save the token info if not already present in the tokens list."""
        if address not in self.tokens:
            self.tokens.append(address)

    @staticmethod
    def validate_address(address: str) -> bool:
        """Validate an Ethereum address."""
        # TODO: Not implemented yet.
        return True

    def sign_transaction(self, tx):
        """
        Sign an Ethereum transaction with the account's private key.

        tx is an instance of the transaction object from a library like web3.eth.account.
        """
        private_key = self.get_private_key_buffer()
        signed_tx = tx.sign(private_key)
        return signed_tx

    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        """Verify if a signed message matches the provided address."""
        public_key = self.recover_signed_msg_public_key(msg, signature)
        actual_address = self.get_address_from_public_key(public_key)
        return to_checksum_address(says_address) == actual_address

    def get_address_from_public_key(self, public_key: str) -> str:
        """Derive the Ethereum address from the public key."""
        # TODO: Needs implementation. We need to make sure a Ethereum private key is derived using hd, then derive address.
        return "Ethereum Address Not Yet Implemented"

    def get_encryption_public_key(self) -> str:
        """Get the public key for encryption."""
        # This is a placeholder. Replace it with the appropriate implementation.
        # For example, if using web3py, you can use `eth_account.Account.encrypt()` for encryption keys.
        raise NotImplementedError("Encryption public key generation is not yet implemented.")