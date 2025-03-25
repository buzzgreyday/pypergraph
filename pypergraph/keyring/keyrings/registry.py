from typing import Union

from pypergraph.core import NetworkId
from ..accounts.dag_account import DagAccount
from ..accounts.eth_account import EthAccount

class KeyringRegistry:
    def __init__(self):
        # Map network values to their respective account classes
        self.registry = {
            NetworkId.Constellation.value: DagAccount,
            NetworkId.Ethereum.value: EthAccount
        }

    def register_account_classes(self, data: dict):
        """
        :param data: { KeyringNetwork.Network.value: AccountClass, ... }
        :return:
        """
        if not data or not isinstance(data, dict):
            raise ValueError(f"KeyringRegistry :: Unsupported type of data: {data}")
        self.registry = data

    def create_account(self, network: str) -> Union[DagAccount, EthAccount]:
        """
        Determine the account class dependent on network.

        :param network: E.g. KeyringNetwork.Constellation.value
        :return: Account class.
        """

        if not network or not isinstance(network, str):
            raise ValueError(f"KeyringRegistry :: Unsupported network: {network}")
        class_ = self.registry.get(network)
        return class_()
