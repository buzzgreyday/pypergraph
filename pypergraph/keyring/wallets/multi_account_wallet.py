from typing import Optional, List, Dict, Any

from pydantic import Field, model_serializer, model_validator, BaseModel

from pypergraph.core import BIP_44_PATHS, KeyringAssetType, KeyringWalletType, NetworkId

from .shared import sid_manager
from ..bip_helpers.bip39_helper import Bip39Helper
from ..keyrings.hd_keyring import HdKeyring


class MultiAccountWallet(BaseModel):

    type: str = Field(default=KeyringWalletType.MultiAccountWallet.value)
    id: str = Field(default=None)
    supported_assets: List[str] = Field(default=[])
    label: Optional[str] = Field(default=None, max_length=12)
    keyring: HdKeyring = Field(default=None)
    mnemonic: Optional[str] = Field(default=None)
    network: str = Field(default=None)

    @model_validator(mode="after")
    def compute_id(self):
        """Automatically computes the id based on injected SID value."""
        self.id = sid_manager.next_sid(self.type)
        return self

    @model_serializer
    def model_serialize(self) -> Dict[str, Any]:
        """Returns a serialized version of the object."""
        return {
            "type": self.type,
            "label": self.label,
            "secret": self.mnemonic,
            "rings": [ring for ring in self.keyring]
        }

    def create(self, network: str, label: str, num_of_accounts: int = 1, mnemonic: str = None):
        """
        Creates a wallet with a keyring of hierarchical deterministic accounts based on the number BIP44 indexes (num_of_accounts).

        :param network: e.g. "Constellation".
        :param label: "New MAW".
        :param num_of_accounts: Number of BIP44 indexes.
        :param mnemonic: Mnemonic phrase.
        """
        bip39 = Bip39Helper()
        mnemonic = mnemonic or bip39.generate_mnemonic()
        if not bip39.is_valid(mnemonic):
            raise ValueError("MultiAccountWallet :: Not a valid mnemonic phrase.")
        self.deserialize(secret=mnemonic, label=label, network=network, num_of_accounts=num_of_accounts)

    def set_label(self, val: str):
        if not val:
            raise ValueError("MultiAccountWallet :: No label set.")
        self.label = val

    def get_label(self) -> str:
        return self.label

    def get_network(self) -> str:
        return self.network

    def get_state(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "supported_assets": self.supported_assets,
            "accounts": [
                {
                    "address": a.get_address(),
                    "network": a.get_network(),
                    "tokens": a.get_tokens(),
                }
                for a in self.get_accounts()
            ],
        }

    def deserialize(self, label: str, network: str, secret: str, num_of_accounts: int, rings: Optional[List] = None):
        # Creates keyring

        keyring = HdKeyring()
        self.set_label(label)
        self.network = network
        self.mnemonic = secret

        if self.network == NetworkId.Constellation.value:
            self.supported_assets.append(KeyringAssetType.DAG.value)
            bip44_path = BIP_44_PATHS.CONSTELLATION_PATH
        else:
            self.supported_assets.append(KeyringAssetType.ETH.value)
            self.supported_assets.append(KeyringAssetType.ERC20.value)
            bip44_path = BIP_44_PATHS.ETH_WALLET_PATH.value

        self.keyring = keyring.create(
            mnemonic=self.mnemonic,
            hd_path=bip44_path,
            network=NetworkId.Constellation.value,
            number_of_accounts=num_of_accounts
        )

        if rings:
            self.keyring.deserialize(rings[0])

    @staticmethod
    def import_account():
        """Importing is not supported."""
        raise ValueError("MultiAccountWallet :: Multi account wallets does not support import account.")

    def get_accounts(self) -> List:
        return self.keyring.get_accounts()

    def get_account_by_address(self, address: str):
        return self.keyring.get_account_by_address(address)

    def add_account(self):
        self.keyring.add_account_at()

    def set_num_of_accounts(self, num: int):
        if not num:
            raise ValueError("MultiAccountWallet :: No number of account specified.")
        keyring = HdKeyring()
        self.keyring = keyring.create(
            mnemonic=self.mnemonic, hd_path=self.keyring.get_hd_path(), network=self.network, number_of_accounts=num
        )

    def remove_account (self, account):
        self.keyring.remove_account(account)

    def export_secret_key(self) -> str:
        return self.mnemonic

    @staticmethod
    def reset_sid():
        sid_manager.reset_sid()