from typing import Optional, List, Dict, Any, Union

from pydantic import Field, model_serializer, model_validator, BaseModel

from pypergraph.core import BIP_44_PATHS, KeyringWalletType, NetworkId

from .shared import sid_manager
from ..accounts.dag_account import DagAccount
from ..accounts.eth_account import EthAccount
from ..bip_helpers.bip39_helper import Bip39Helper
from ..keyrings.hd_keyring import HdKeyring


class MultiChainWallet(BaseModel):
    type: str = Field(default=KeyringWalletType.MultiChainWallet.value)
    id: str = Field(default=None)
    supported_assets: List[str] = Field(default=[])
    label: Optional[str] = Field(default=None, max_length=12)
    keyrings: List[HdKeyring] = Field(default=[])
    mnemonic: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def compute_id(self):
        """Automatically computes the id based on injected SID value."""
        self.id = sid_manager.next_sid(self.type)
        return self

    @model_serializer
    def model_serialize(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "label": self.label,
            "secret": self.mnemonic,
            "rings": [ring.model_dump() for ring in self.keyrings]
        }

    def create(self, label: str, mnemonic: Optional[str] = None, rings: Optional[list] = None):
        """
        If mnemonic is set, restore the wallet. Else, generate mnemonic and create new wallet.

        :param label: Name of the wallet.
        :param mnemonic: Seed phrase.
        :param rings: Keyrings.
        """
        bip39 = Bip39Helper()
        self.label = label
        self.mnemonic = mnemonic or bip39.generate_mnemonic()
        if not bip39.is_valid(mnemonic):
            raise ValueError("MultiAccountWallet :: Not a valid mnemonic phrase.")
        self.deserialize(secret=mnemonic, label=label, rings=rings)


    def set_label(self, label: str):
        """
        Set the name of the wallet.

        :param label:
        :return:
        """
        if not label:
            raise ValueError("MultiChainWallet :: No label set.")
        self.label = label

    def get_label(self) -> str:
        """
        Get the name on the wallet.

        :return:
        """
        return self.label

    @staticmethod
    def get_network():
        raise ValueError("MultiChainWallet :: Does not support this method")

    def get_state(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "supported_assets": self.supported_assets,
            "accounts": [
                {
                    "address": a.get_address(),
                    "network": a.get_network_id(),
                    "tokens": a.get_tokens(),
                }
                for a in self.get_accounts()
            ],
        }

    @staticmethod
    def import_account():
        """Importing account is not supported."""
        raise ValueError("MultiChainWallet :: Multi chain wallet does not support importing account.")

    # TODO
    # getAssets(): string[]
    #{
    # return this.keyrings.reduce < string[] > ((res, w) = > res.concat(w.getAssetList()), []);
    #}

    def get_accounts(self) -> List[Union[DagAccount, EthAccount]]: # IKeyringAccount
        return [account for keyring in self.keyrings for account in keyring.get_accounts()]

    def get_account_by_address(self, address: str) -> Union[DagAccount, EthAccount]: # IKeyringAccount
        account = None
        for keyring in self.keyrings:
            account = keyring.get_account_by_address(address)
            if account:
                break
        return account

    @staticmethod
    def remove_account(): # IKeyAccount {
        raise ValueError("MultiChainWallet :: Does not allow removing accounts.")

    def export_secret_key(self) -> str:
        return self.mnemonic

    def deserialize(self, label: str, secret: str, rings: Optional[list] = None):
        """
        Create keyrings.

        :param label:
        :param secret:
        :param rings:
        :return:
        """

        self.set_label(label)
        self.mnemonic = secret

        self.keyrings = [
            HdKeyring().create(mnemonic=self.mnemonic, hd_path=BIP_44_PATHS.CONSTELLATION_PATH.value, network=NetworkId.Constellation.value, number_of_accounts=1),
            HdKeyring().create(mnemonic=self.mnemonic, hd_path=BIP_44_PATHS.ETH_WALLET_PATH.value, network=NetworkId.Ethereum.value, number_of_accounts=1)
        ]

        if rings:
            for i, r in enumerate(rings):
                self.keyrings[i].deserialize(r)

    @staticmethod
    def reset_sid():
        sid_manager.reset_sid()