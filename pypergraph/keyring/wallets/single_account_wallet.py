import re
from typing import Optional, List, Dict, Any, Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from pydantic import Field, model_serializer, model_validator, BaseModel

from pypergraph.core import KeyringAssetType, KeyringWalletType, NetworkId

from .shared import sid_manager
from ..accounts.dag_account import DagAccount
from ..accounts.eth_account import EthAccount
from ..keyrings.simple_keyring import SimpleKeyring

class SingleAccountWallet(BaseModel):

    type: str = Field(default=KeyringWalletType.SingleAccountWallet.value)
    id: str = Field(default=None)
    supported_assets: List = Field(default_factory=list)
    label: Optional[str] = Field(default=None, max_length=12)
    keyring: Optional[Any] = Field(default=None)
    network: Optional[str] = Field(default=None)

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
            "network": self.network,
            "secret": self.export_secret_key(),
        }

    def create(self, network: str, label: str, private_key: str = None):
        """
        Initiates the creation of a new single key wallet.

        :param network:
        :param private_key:
        :param label:
        :return:
        """

        private_key = private_key or ec.generate_private_key(curve=ec.SECP256K1(), backend=default_backend()).private_numbers().private_value.to_bytes(32, byteorder='big').hex()
        valid = re.fullmatch(r"^[a-fA-F0-9]{64}$", private_key)
        if not valid:
            ValueError("SingleAccountWallet :: Private key is invalid.")
        self.deserialize(label=label, network=network, secret=private_key)

    def set_label(self, label: str):
        """
        Set the name of the wallet.

        :param label:
        :return:
        """
        if not label:
            raise ValueError("SingleAccountWallet :: No label set.")
        self.label = label

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
                    "network": a.get_network_id(),
                    "tokens": a.get_tokens(),
                }
                for a in self.get_accounts()
            ],
        }

    def deserialize(self, network: str, label: str, secret: str):
        """
        Create keyring.

        :param network:
        :param label:
        :param secret:
        :return:
        """
        self.set_label(label)
        self.network = network or NetworkId.Constellation.value
        self.keyring = SimpleKeyring()

        self.keyring.deserialize(network=self.network, accounts=[{ "private_key": secret }])

        if self.network == NetworkId.Ethereum.value:
          self.supported_assets.append(KeyringAssetType.ETH.value)
          self.supported_assets.append(KeyringAssetType.ERC20.value)

        elif self.network == NetworkId.Constellation.value:
          self.supported_assets.append(KeyringAssetType.DAG.value)

    @staticmethod
    def import_account ():
        """Not supported for SingleAccountWallet"""
        raise ValueError("SingleAccountWallet :: does not support importing of account.")

    def get_accounts(self) -> List[Union[DagAccount, EthAccount]]:
        return self.keyring.get_accounts()

    def get_account_by_address(self, address: str) -> Union[DagAccount, EthAccount]:
        return self.keyring.get_account_by_address(address)

    def remove_account(self, account):
        raise ValueError("SingleChainWallet :: Does not allow removing accounts.")

    def export_secret_key(self) -> str:
        return self.keyring.get_accounts()[0].wallet.private_numbers().private_value.to_bytes(32, 'big').hex()

    @staticmethod
    def reset_sid():
        sid_manager.reset_sid()