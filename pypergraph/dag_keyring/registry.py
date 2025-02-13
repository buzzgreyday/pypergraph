from pypergraph.dag_core import NetworkId
from .accounts import DagAccount, EthAccount


# Polymorphism

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
        if not data or type(data) is not dict:
            raise ValueError(f"KeyringRegistry :: Unsupported type of data: {data}")
        self.registry = data

    def create_account(self, network: str):
        """
        Determine the account class dependent on network.

        :param network: E.g. KeyringNetwork.Constellation.value
        :return: Account class.
        """

        if not network or type(network) is not str:
            raise ValueError(f"KeyringRegistry :: Unsupported network: {network}")
        class_ = self.registry.get(network)
        return class_()
