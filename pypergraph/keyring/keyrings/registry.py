from typing import Dict

from pypergraph.core import NetworkId
from ..accounts.dag_account import DagAccount
from ..accounts.ecdsa_account import EcdsaAccount
from ..accounts.eth_account import EthAccount


class AccountRegistry:
    def __init__(self):
        self.registry: Dict[str:EcdsaAccount] = {
            NetworkId.Constellation.value: DagAccount,
            NetworkId.Ethereum.value: EthAccount,
        }

    def register_account_classes(self, data: dict):
        """
        :param data: { KeyringNetwork.Network.value: AccountClass, ... }
        :return:
        """
        if not data or not isinstance(data, dict):
            raise ValueError(f"KeyringRegistry :: Unsupported type of data: {data}")
        self.registry = data

    def create_account(self, network: str) -> EcdsaAccount:
        """
        Determine the account class dependent on network.

        :param network: E.g. KeyringNetwork.Constellation.value
        :return: Account class.
        """

        if not network or not isinstance(network, str):
            raise ValueError(f"KeyringRegistry :: Unsupported network: {network}")
        class_ = self.registry.get(network)
        return class_()

    def add_account(self, network: str, account: EcdsaAccount):
        """
        Add account to registry.

        :param network: New chain name (network id).
        :param account: New account inheriting from EcdsaAccount.
        """
        self.registry[network] = account


account_registry = AccountRegistry()
