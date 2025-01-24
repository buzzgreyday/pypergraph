from pypergraph.dag_core import KeyringNetwork
from pypergraph.dag_keyring.accounts import DagAccount, EcdsaAccount

# Polymorphism

class KeyringRegistry:
    def __init__(self):
        # Map network values to their respective account classes
        self.registry = {
            KeyringNetwork.Constellation.value: DagAccount,
            KeyringNetwork.Ethereum.value: EcdsaAccount,
        }

    def register_account_classes(self, data: dict):
        """
        :param data: { KeyringNetwork.Network.value: AccountClass, ... }
        :return:
        """
        self.registry = data

    def create_account(self, network):
        """
        Determine the account class dependent on network.
        :param network: E.g. KeyringNetwork.Constellation.value
        :return: Account class.
        """

        if not network:
            raise ValueError(f"Unsupported network: {network}")
        class_ = self.registry.get(network)
        return class_()

