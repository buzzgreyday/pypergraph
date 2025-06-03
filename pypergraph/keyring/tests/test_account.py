import hashlib
from typing import List

from pypergraph.keyring.accounts.ecdsa_account import EcdsaAccount


class CustomAccount(EcdsaAccount):

    @property
    def decimals(self) -> int:
        return 8

    @property
    def network_id(self) -> str:
        return "Custom"

    @property
    def has_token_support(self) -> bool:
        return False

    @property
    def supported_assets(self) -> List[str]:
        return ["FAKE1", "FAKE2"]

    @staticmethod
    def validate_address(address: str) -> bool:
        return True

    def get_public_key(self) -> str:
        return "FAKE_PUBLIC_KEY"

    def get_address(self) -> str:
        return self.get_address_from_public_key()

    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        raise NotImplementedError("TEST ACCOUNT")

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def get_address_from_public_key(self) -> str:

        return "FAKE_ADDRESS"