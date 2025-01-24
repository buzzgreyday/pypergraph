from ecdsa import SigningKey, SECP256k1
from eth_account import Account

from pypergraph.dag_core import KeyringNetwork
from .accounts import DagAccount, EthAccount


# Polymorphism

class KeyringRegistry:
    def __init__(self):
        # Map network values to their respective account classes
        self.registry = {
            KeyringNetwork.Constellation.value: DagAccount,
            KeyringNetwork.Ethereum.value: EthAccount
        }

    def register_account_classes(self, data: dict):
        """
        :param data: { KeyringNetwork.Network.value: AccountClass, ... }
        :return:
        """
        if not data or type(data) != dict:
            raise ValueError(f"KeyringRegistry :: Unsupported type of data: {data}")
        self.registry = data

    def create_account(self, network: str):
        """
        Determine the account class dependent on network.

        :param network: E.g. KeyringNetwork.Constellation.value
        :return: Account class.
        """

        if not network or type(network) != str:
            raise ValueError(f"KeyringRegistry :: Unsupported network: {network}")
        class_ = self.registry.get(network)
        return class_()
