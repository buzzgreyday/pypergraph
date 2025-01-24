from pypergraph.dag_core import KeyringNetwork
from pypergraph.dag_keyring.accounts import DagAccount, EcdsaAccount

class KeyringRegistry:
    def __init__(self):
        # Map network values to their respective handler classes
        self.registry = {
            KeyringNetwork.Constellation.value: DagAccount,
            KeyringNetwork.Ethereum.value: EcdsaAccount,
        }

    def create_account(self, network):

        if not network:
            raise ValueError(f"Unsupported network: {network}")
        class_ = self.registry.get(network)
        print(class_)
        return class_()  # Store the chosen handler instance

